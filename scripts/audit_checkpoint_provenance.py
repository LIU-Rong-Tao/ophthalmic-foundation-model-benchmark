#!/usr/bin/env python3
"""Audit checkpoint provenance using official upstream evidence without downloading weights."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import os
import re
import ssl
import subprocess
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import requests
import yaml
from audit_checkpoint_access import audit_checkpoint, google_drive_file_id, utc_now

from ophbench import load_registry

PROVENANCE_STATUSES = {
    "official_source_verified",
    "author_source_probable",
    "third_party_mirror",
    "source_ambiguous",
    "source_not_found",
    "authentication_required",
    "probe_inconclusive",
}
CONFIDENCE_LEVELS = {"high", "medium", "low"}
SENSITIVE_PATTERN = re.compile(
    r"(?i)(bearer\s+[A-Za-z0-9._-]+|(?:hf|ghp|github|access)[_-]?token\s*[=:]\s*[^\s,;]+)"
)
SECRET_QUERY_KEYS = {
    "token",
    "access_token",
    "auth",
    "authorization",
    "cookie",
    "signature",
    "policy",
    "key-pair-id",
    "x-amz-credential",
    "x-amz-signature",
    "x-goog-credential",
    "x-goog-signature",
}


@dataclass
class ProvenanceRow:
    model_id: str
    checkpoint_id: str
    registered_url: str | None
    resolved_url: str | None
    official_paper_url: str | None
    official_code_url: str | None
    official_project_url: str | None
    weight_evidence_url: str | None
    evidence_source_type: str
    repository_owner: str | None
    checkpoint_provider_owner: str | None
    exact_checkpoint_name: str
    exact_filename: str | None
    source_commit_or_release: str | None
    model_modality: str
    checkpoint_modality: str
    license_url: str | None
    license_status: str
    evidence_summary: str
    provenance_status: str
    confidence: str
    manual_review_reason: str | None
    link_reachable: bool
    file_verified: bool
    adapter_smoke_passed: bool
    checked_at: str
    access_diagnostic: str | None
    previous_access_status: str | None


def sanitize_text(value: Any) -> str:
    return SENSITIVE_PATTERN.sub("[REDACTED]", str(value or ""))


def sanitize_url(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urlparse(url)
    query = [
        (
            key,
            "[REDACTED]"
            if key.lower() in SECRET_QUERY_KEYS or key.lower().endswith("signature")
            else value,
        )
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
    ]
    return urlunparse(parsed._replace(query=urlencode(query)))


def sanitize_resolved_url(url: str | None) -> str | None:
    sanitized = sanitize_url(url)
    if not sanitized:
        return None
    parsed = urlparse(sanitized)
    host = parsed.netloc.lower()
    if "xet-bridge" in host or host.endswith("cdn.hf.co"):
        return urlunparse(parsed._replace(query=""))
    return sanitized


def url_identity(url: str | None) -> tuple[str, ...] | None:
    if not url:
        return None
    parsed = urlparse(html.unescape(url))
    host = parsed.netloc.lower().removeprefix("www.")
    path = parsed.path.strip("/")
    if host in {"drive.google.com", "drive.usercontent.google.com"}:
        file_id = google_drive_file_id(url)
        return ("google_drive", file_id) if file_id else None
    if host == "huggingface.co":
        parts = path.split("/")
        return ("huggingface", *parts[:2]) if len(parts) >= 2 else None
    if host == "zenodo.org":
        match = re.search(r"(?:records|record)/(\d+)", path)
        return ("zenodo", match.group(1)) if match else None
    if host == "github.com":
        match = re.search(r"^([^/]+)/([^/]+)/releases/(?:tag|download)/([^/]+)", path)
        if match:
            return ("github_release", *match.groups())
    return ("url", host, path.rstrip("/").lower())


def extract_urls(markdown: str) -> list[str]:
    candidates = re.findall(r"https?://[^\s<>'\"]+", markdown)
    return [html.unescape(item).rstrip(".,;:!?)]}") for item in candidates]


def first_heading(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return sanitize_text(line[2:].strip())
    return fallback


def git_head(code_url: str) -> tuple[str | None, str | None]:
    result = subprocess.run(
        ["git", "ls-remote", "--symref", f"{code_url}.git", "HEAD"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if result.returncode != 0:
        return None, None
    branch = None
    commit = None
    for line in result.stdout.splitlines():
        if line.startswith("ref:") and line.endswith("\tHEAD"):
            branch = line.split()[1].removeprefix("refs/heads/")
        elif line.endswith("\tHEAD"):
            commit = line.split()[0]
    return branch, commit


def fetch_official_readme(
    code_url: str, *, session: requests.Session
) -> tuple[str | None, str | None, str | None, str | None]:
    parsed = urlparse(code_url)
    parts = parsed.path.strip("/").split("/")
    if parsed.netloc.lower() != "github.com" or len(parts) < 2:
        return None, None, None, "official code URL is not a GitHub repository"
    owner, repo = parts[:2]
    branch, commit = git_head(code_url)
    refs = [item for item in [commit, branch, "main", "master"] if item]
    seen: set[str] = set()
    errors: list[str] = []
    for ref in refs:
        if ref in seen:
            continue
        seen.add(ref)
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/README.md"
        try:
            response = session.get(raw_url, timeout=(10, 30))
            if response.status_code == 200:
                revision = commit or (
                    f"{ref}@readme-sha256:{hashlib.sha256(response.content).hexdigest()}"
                )
                return response.text, raw_url, revision, None
            errors.append(f"HTTP {response.status_code} for {ref}")
        except requests.RequestException as exc:
            errors.append(f"{type(exc).__name__} for {ref}")
    return None, None, commit, "; ".join(errors) or "README unavailable"


def reference_matches(
    registered_url: str | None, markdown: str, extra_patterns: list[str] | None = None
) -> bool:
    target = url_identity(registered_url)
    if not target:
        return False
    identities = {identity for item in extract_urls(markdown) if (identity := url_identity(item))}
    if target in identities:
        return True
    if target[0] == "huggingface" and "/".join(target[1:]) in markdown:
        return True
    return any(pattern in markdown for pattern in (extra_patterns or []))


def provider_owner(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urlparse(url)
    host = parsed.netloc.lower().removeprefix("www.")
    parts = parsed.path.strip("/").split("/")
    if host in {"huggingface.co", "github.com"} and parts:
        return parts[0]
    if host == "zenodo.org":
        return "Zenodo record creators"
    if host in {"drive.google.com", "drive.usercontent.google.com"}:
        return "not exposed by public Google Drive URL"
    return host or None


def classify_provenance(
    *,
    repository_class: str,
    exact_reference: bool,
    registered_url: str | None,
    access_status: str | None,
    evidence_fetch_ok: bool,
    model_id: str,
) -> tuple[str, str]:
    if not registered_url:
        return "source_not_found", "low"
    if not evidence_fetch_ok:
        return "probe_inconclusive", "low"
    if exact_reference and access_status == "authentication_required":
        return "authentication_required", "high"
    if model_id == "mirage" and access_status == "probe_failed":
        return "probe_inconclusive", "medium"
    if exact_reference and repository_class == "official":
        return "official_source_verified", "high"
    if exact_reference and repository_class == "author":
        return "author_source_probable", "medium"
    if repository_class == "third_party":
        return "third_party_mirror", "medium" if exact_reference else "low"
    return "source_ambiguous", "low"


def checkpoint_verification(checkpoint: Any, field: str) -> bool:
    verification = getattr(checkpoint, "verification", None)
    return bool(verification and getattr(verification, field, None) == "verified")


def read_access_rows(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return {row["checkpoint_id"]: row for row in csv.DictReader(handle)}


def retry_inconclusive_access(
    checkpoint: Any,
    access: dict[str, str],
    *,
    session: requests.Session,
) -> tuple[dict[str, str], str | None]:
    if access.get("access_status") != "probe_failed":
        return access, None
    with requests.Session() as retry_session:
        retry = audit_checkpoint(
            checkpoint,
            session=retry_session,
            hf_token=os.getenv("HF_TOKEN"),
        )
    diagnostic = f"previous={access.get('failure_reason')}; retry={retry.access_status}"
    if checkpoint.model_id == "mirage":
        verify_paths = ssl.get_default_verify_paths()
        proxy_configured = bool(os.getenv("HTTPS_PROXY") or os.getenv("https_proxy"))
        diagnostic += (
            f"; ca_file={verify_paths.cafile or 'system-default'}; "
            f"proxy_configured={str(proxy_configured).lower()}; ssl_verification=enabled"
        )
    merged = dict(access)
    merged.update(
        {
            "resolved_url": retry.resolved_url or access.get("resolved_url", ""),
            "access_status": retry.access_status,
            "server_accessible": str(retry.server_accessible),
            "actual_filename": retry.actual_filename or access.get("actual_filename", ""),
            "failure_reason": retry.failure_reason or "",
        }
    )
    return merged, sanitize_text(diagnostic)


def github_rate_limit_diagnostic(url: str | None, *, session: requests.Session) -> str | None:
    if not url or "github.com" not in url or "/releases/tag/" not in url:
        return None
    match = re.search(r"github\.com/([^/]+)/([^/]+)/releases/tag/([^/?#]+)", url)
    if not match:
        return None
    owner, repo, tag = match.groups()
    response = session.get(
        f"https://api.github.com/repos/{owner}/{repo}/releases/tags/{tag}",
        headers={"Accept": "application/vnd.github+json"},
        timeout=(10, 30),
    )
    reset = response.headers.get("x-ratelimit-reset")
    remaining = response.headers.get("x-ratelimit-remaining", "unknown")
    reset_at = "unavailable"
    if reset and reset.isdigit():
        reset_at = datetime.fromtimestamp(int(reset), tz=timezone.utc).isoformat()
    if response.status_code == 403:
        return f"GitHub API rate limited; remaining={remaining}; reset_at={reset_at}"
    return f"GitHub API HTTP {response.status_code}; remaining={remaining}; reset_at={reset_at}"


def manual_reason(status: str, license_status: str, diagnostic: str | None) -> str | None:
    if status == "authentication_required":
        return "官方来源已确认，但当前服务器尚未获得权重访问授权。"
    if status == "probe_inconclusive":
        return f"网络或服务探测未形成结论。{diagnostic or ''}".strip()
    if status not in {"official_source_verified"}:
        return "官方材料与登记入口之间尚未形成完整、精确的证据链。"
    if license_status == "not_declared" or "scope_unverified" in license_status:
        return "来源已核验，但权重许可证或许可证适用范围仍需人工确认。"
    return None


def manual_action(row: ProvenanceRow, run_command: str) -> dict[str, Any]:
    auth = row.provenance_status == "authentication_required"
    license_review = "license" in (row.manual_review_reason or "").lower() or "许可证" in (
        row.manual_review_reason or ""
    )
    if auth:
        action = "用机构邮箱完成官方 Hugging Face 访问申请并在服务器安全配置 HF_TOKEN。"
    elif row.provenance_status == "probe_inconclusive":
        action = "检查服务器 CA、代理或外部服务限流状态后重新运行 provenance audit。"
    elif license_review:
        action = "阅读官方 LICENSE/README，确认许可证是否覆盖模型权重及计划用途。"
    else:
        action = "从论文或官方项目页补充指向该准确 checkpoint 的一级证据。"
    return {
        "checkpoint_id": row.checkpoint_id,
        "current_blocker": row.manual_review_reason or "manual confirmation required",
        "required_user_action": action,
        "official_entry": row.official_project_url or row.official_code_url or "",
        "login_required": auth,
        "license_acceptance_required": auth,
        "application_required": auth,
        "next_command": run_command,
    }


def build_rows(
    *,
    snapshot: Any,
    access_rows: dict[str, dict[str, str]],
    evidence_config: dict[str, Any],
    session: requests.Session,
) -> tuple[list[ProvenanceRow], list[dict[str, Any]]]:
    models = {item.model_id: item for item in snapshot.models}
    readmes: dict[str, tuple[str | None, str | None, str | None, str | None]] = {}
    rows: list[ProvenanceRow] = []
    evidence_index: list[dict[str, Any]] = []
    for checkpoint in snapshot.checkpoints:
        model = models[checkpoint.model_id]
        config = evidence_config["models"][checkpoint.model_id]
        if checkpoint.model_id not in readmes:
            readmes[checkpoint.model_id] = fetch_official_readme(
                str(model.code_url), session=session
            )
        markdown, evidence_url, commit, fetch_error = readmes[checkpoint.model_id]
        access = access_rows.get(checkpoint.checkpoint_id, {})
        previous_access_status = access.get("access_status")
        access, diagnostic = retry_inconclusive_access(checkpoint, access, session=session)
        if checkpoint.model_id == "retfound-green":
            rate_detail = github_rate_limit_diagnostic(checkpoint.weight_url, session=session)
            diagnostic = "; ".join(item for item in [diagnostic, rate_detail] if item)
            if rate_detail and "GitHub API HTTP 200" in rate_detail:
                access["access_status"] = "accessible_source_unverified"
                access["server_accessible"] = "True"
        exact_reference = bool(
            markdown
            and reference_matches(
                checkpoint.weight_url,
                markdown,
                config.get("weight_reference_patterns"),
            )
        )
        status, confidence = classify_provenance(
            repository_class=config["repository_class"],
            exact_reference=exact_reference,
            registered_url=checkpoint.weight_url,
            access_status=access.get("access_status"),
            evidence_fetch_ok=markdown is not None,
            model_id=checkpoint.model_id,
        )
        if status not in PROVENANCE_STATUSES or confidence not in CONFIDENCE_LEVELS:
            raise RuntimeError("invalid provenance decision")
        license_status = config.get("license_status", "unknown")
        summary = config["evidence_summary"]
        if not exact_reference:
            summary += " 本次抓取的官方材料中未精确匹配登记入口。"
        if fetch_error:
            summary += f" 证据页抓取异常：{sanitize_text(fetch_error)}。"
        row = ProvenanceRow(
            model_id=checkpoint.model_id,
            checkpoint_id=checkpoint.checkpoint_id,
            registered_url=sanitize_url(checkpoint.weight_url),
            resolved_url=sanitize_resolved_url(access.get("resolved_url") or None),
            official_paper_url=sanitize_url(model.paper_url),
            official_code_url=sanitize_url(model.code_url),
            official_project_url=sanitize_url(config.get("official_project_url")),
            weight_evidence_url=sanitize_url(evidence_url),
            evidence_source_type=config["evidence_source_type"],
            repository_owner=config.get("repository_owner"),
            checkpoint_provider_owner=provider_owner(checkpoint.weight_url),
            exact_checkpoint_name=checkpoint.checkpoint_name,
            exact_filename=(
                access.get("actual_filename")
                or evidence_config.get("checkpoints", {})
                .get(checkpoint.checkpoint_id, {})
                .get("exact_filename")
            ),
            source_commit_or_release=(
                url_identity(checkpoint.weight_url)[-1]
                if checkpoint.provider == "github_release" and url_identity(checkpoint.weight_url)
                else commit
            ),
            model_modality=";".join(model.modalities),
            checkpoint_modality=";".join(checkpoint.modalities),
            license_url=sanitize_url(config.get("license_url")),
            license_status=license_status,
            evidence_summary=sanitize_text(summary),
            provenance_status=status,
            confidence=confidence,
            manual_review_reason=manual_reason(status, license_status, diagnostic),
            link_reachable=access.get("access_status")
            in {"verified_accessible", "accessible_source_unverified", "authentication_required"},
            file_verified=bool(checkpoint.sha256)
            and checkpoint_verification(checkpoint, "checkpoint_file"),
            adapter_smoke_passed=checkpoint_verification(checkpoint, "adapter"),
            checked_at=utc_now(),
            access_diagnostic=sanitize_text(diagnostic) if diagnostic else None,
            previous_access_status=previous_access_status,
        )
        rows.append(row)
        evidence_index.append(
            {
                "model_id": row.model_id,
                "checkpoint_id": row.checkpoint_id,
                "supporting_url": row.weight_evidence_url,
                "evidence_type": row.evidence_source_type,
                "fetched_at": row.checked_at,
                "page_title": first_heading(markdown or "", model.model_name),
                "evidence_summary": row.evidence_summary,
            }
        )
    return rows, evidence_index


def write_csv(path: Path, payload: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(payload)


def render_html(rows: list[ProvenanceRow], counts: Counter[str]) -> str:
    summary = "".join(
        f"<li><code>{html.escape(status)}</code>: {count}</li>"
        for status, count in sorted(counts.items())
    )
    table_rows = "".join(
        "<tr>"
        f"<td>{html.escape(row.model_id)}</td>"
        f"<td>{html.escape(row.checkpoint_id)}</td>"
        f"<td>{html.escape(row.provenance_status)}</td>"
        f"<td>{html.escape(row.confidence)}</td>"
        f"<td>{'是' if row.link_reachable else '否'}</td>"
        f"<td>{'是' if row.file_verified else '否'}</td>"
        f"<td>{'是' if row.adapter_smoke_passed else '否'}</td>"
        f"<td>{html.escape(row.evidence_summary)}</td>"
        "</tr>"
        for row in rows
    )
    return (
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
        "<title>Checkpoint 官方来源证据审计</title><style>"
        "body{font-family:system-ui,sans-serif;margin:2rem;color:#172033}"
        "table{border-collapse:collapse;width:100%;font-size:14px}"
        "th,td{border:1px solid #d8dee9;padding:8px;vertical-align:top}"
        "th{background:#f3f6fa;text-align:left}"
        "code{background:#eef2f7;padding:2px 4px}</style></head>"
        f"<body><h1>Checkpoint 官方来源证据审计</h1>"
        f"<p>总 checkpoint：{len(rows)}</p><ul>{summary}</ul>"
        "<p>以下四项独立记录：链接可达、官方来源、文件核验、Adapter smoke；"
        "任何一项均不会自动推导另一项。</p>"
        "<table><thead><tr><th>模型</th><th>Checkpoint</th><th>来源状态</th>"
        "<th>置信度</th><th>链接可达</th><th>文件核验</th>"
        "<th>Adapter smoke</th><th>证据摘要</th></tr></thead>"
        f"<tbody>{table_rows}</tbody></table></body></html>"
    )


def write_outputs(
    *,
    run_dir: Path,
    rows: list[ProvenanceRow],
    evidence_index: list[dict[str, Any]],
    access_path: Path,
    evidence_path: Path,
    run_id: str,
) -> None:
    run_dir.mkdir(parents=True, exist_ok=False)
    payload = [asdict(row) for row in rows]
    fields = list(ProvenanceRow.__annotations__)
    write_csv(run_dir / "checkpoint_provenance.csv", payload, fields)
    (run_dir / "checkpoint_provenance.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    command = f"python scripts/audit_checkpoint_provenance.py --run-id {run_id}-retry"
    manual = [manual_action(row, command) for row in rows if row.manual_review_reason]
    manual_fields = [
        "checkpoint_id",
        "current_blocker",
        "required_user_action",
        "official_entry",
        "login_required",
        "license_acceptance_required",
        "application_required",
        "next_command",
    ]
    write_csv(run_dir / "manual_review.csv", manual, manual_fields)
    counts = Counter(row.provenance_status for row in rows)
    transitions = Counter(row.provenance_status for row in rows if row.link_reachable)
    server_accessible_transitions = Counter(
        row.provenance_status
        for row in rows
        if row.previous_access_status in {"verified_accessible", "accessible_source_unverified"}
    )
    summary = {
        "run_id": run_id,
        "checkpoint_count": len(rows),
        "status_counts": dict(sorted(counts.items())),
        "previously_link_reachable_transition_counts": dict(sorted(transitions.items())),
        "previously_server_accessible_transition_counts": dict(
            sorted(server_accessible_transitions.items())
        ),
        "manual_review_count": len(manual),
        "separation_invariants": {
            "link_reachable_is_independent": True,
            "official_source_verified_is_independent": True,
            "file_verified_is_independent": True,
            "adapter_smoke_passed_is_independent": True,
        },
    }
    (run_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (run_dir / "evidence_index.json").write_text(
        json.dumps(evidence_index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    config = {
        "run_id": run_id,
        "audit_type": "checkpoint_provenance",
        "registry_api": "ophbench.load_registry",
        "access_audit_input": str(access_path),
        "evidence_config": str(evidence_path),
        "download_weights": False,
        "ssl_verification": True,
        "authentication_values_recorded": False,
    }
    (run_dir / "run_config.yaml").write_text(
        yaml.safe_dump(config, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    (run_dir / "report.html").write_text(render_html(rows, counts), encoding="utf-8")
    serialized = "\n".join(path.read_text(encoding="utf-8") for path in run_dir.iterdir())
    if SENSITIVE_PATTERN.search(serialized):
        raise RuntimeError("sensitive authentication material detected in audit outputs")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--access-audit",
        type=Path,
        default=Path("artifacts/checkpoint_access_audit/checkpoint_access_audit.csv"),
    )
    parser.add_argument(
        "--evidence-config",
        type=Path,
        default=Path("audits/checkpoint_provenance/source_evidence.yaml"),
    )
    parser.add_argument("--output-root", type=Path, default=Path("audits/checkpoint_provenance"))
    parser.add_argument("--run-id", default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    args = parser.parse_args()
    snapshot = load_registry()
    access_rows = read_access_rows(args.access_audit)
    evidence_config = yaml.safe_load(args.evidence_config.read_text(encoding="utf-8"))
    if set(evidence_config["models"]) != {item.model_id for item in snapshot.models}:
        raise RuntimeError("evidence config must cover every registered model exactly once")
    session = requests.Session()
    rows, index = build_rows(
        snapshot=snapshot,
        access_rows=access_rows,
        evidence_config=evidence_config,
        session=session,
    )
    if len(rows) != snapshot.checkpoint_count:
        raise RuntimeError("provenance audit did not emit one row per checkpoint")
    run_dir = args.output_root / args.run_id
    write_outputs(
        run_dir=run_dir,
        rows=rows,
        evidence_index=index,
        access_path=args.access_audit,
        evidence_path=args.evidence_config,
        run_id=args.run_id,
    )
    print(f"Audited {len(rows)} checkpoint provenance records -> {run_dir}")


if __name__ == "__main__":
    main()
