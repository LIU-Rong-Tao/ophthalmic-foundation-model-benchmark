#!/usr/bin/env python3
"""Audit code-license and weight-license evidence for review-required checkpoints."""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
import yaml

from ophbench import load_registry

LICENSE_STATUSES = {
    "license_verified",
    "license_review_required",
    "license_probe_inconclusive",
}


def read_csv(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return {row["checkpoint_id"]: row for row in csv.DictReader(handle)}


def sanitize_text(value: str | None) -> str:
    return re.sub(r"(?i)(bearer\s+\S+|(?:token|cookie|signature)=\S+)", "[REDACTED]", value or "")


def page_title(text: str, fallback: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
    if match:
        return html.unescape(re.sub(r"\s+", " ", match.group(1))).strip()[:200]
    for line in text.splitlines():
        if line.startswith("# "):
            return sanitize_text(line[2:].strip())[:200]
    return fallback


def fetch_evidence(session: requests.Session, url: str | None) -> dict[str, Any]:
    if not url:
        return {
            "url": None,
            "reachable": False,
            "status_code": None,
            "title": "",
            "error": "not_declared",
        }
    try:
        response = session.get(url, timeout=(10, 30), stream=True)
        status_code = response.status_code
        content = next(response.iter_content(chunk_size=65536), b"")
        response.close()
        text = content.decode("utf-8", errors="replace")
        return {
            "url": url,
            "reachable": 200 <= status_code < 400,
            "status_code": status_code,
            "title": page_title(text, urlparse(url).path.rsplit("/", 1)[-1] or url),
            "error": None if 200 <= status_code < 400 else f"HTTP {status_code}",
        }
    except requests.RequestException as exc:
        return {
            "url": url,
            "reachable": False,
            "status_code": None,
            "title": "",
            "error": f"{type(exc).__name__}: {exc}",
        }


def project_readme_url(project_url: str) -> str:
    parsed = urlparse(project_url)
    parts = [item for item in parsed.path.strip("/").split("/") if item]
    if parsed.netloc.lower().endswith("github.com") and len(parts) >= 2:
        return f"https://raw.githubusercontent.com/{parts[0]}/{parts[1]}/HEAD/README.md"
    return project_url


def raw_license_url(license_url: str | None) -> str | None:
    if not license_url:
        return None
    parsed = urlparse(license_url)
    parts = [item for item in parsed.path.strip("/").split("/") if item]
    if parsed.netloc.lower().endswith("github.com") and len(parts) >= 5 and parts[2] == "blob":
        return f"https://raw.githubusercontent.com/{parts[0]}/{parts[1]}/{'/'.join(parts[3:])}"
    return license_url


def classify_license(
    *, code_evidence: dict[str, Any], registered_status: str, weight_reachable: bool
) -> tuple[str, str, str, str]:
    code_status = (
        "declared_code_license_page_reachable"
        if code_evidence["reachable"]
        else "code_license_not_verified"
    )
    if registered_status in {
        "apache-2.0_code_and_weights_declared",
        "cc-by-4.0_models_and_code_declared",
    }:
        weight_status = "explicit_weight_terms_declared"
        if code_evidence["reachable"] and weight_reachable:
            return (
                "license_verified",
                code_status,
                weight_status,
                "代码许可证和权重许可均有登记证据。",
            )
    elif (
        "research_and_education_only" in registered_status
        or "academic_research_only" in registered_status
    ):
        weight_status = "restricted_research_scope_declared"
    elif "weight_access_terms_required" in registered_status:
        weight_status = "access_terms_required"
    elif "weight_scope_unverified" in registered_status:
        weight_status = "weight_scope_unverified"
    else:
        weight_status = "weight_license_not_declared"
    reason = "代码许可证与权重使用范围不能视为同一许可。"
    if not code_evidence["reachable"]:
        reason += " 官方 LICENSE 页面本轮未成功核验。"
    if not weight_reachable:
        reason += " 权重入口未形成可直接核验许可证的证据。"
    return "license_review_required", code_status, weight_status, reason


def build_rows(
    *,
    plan_rows: dict[str, dict[str, str]],
    provenance_rows: dict[str, dict[str, str]],
    evidence_config: dict[str, Any],
    snapshot: Any,
    session: requests.Session,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    checkpoints = {item.checkpoint_id: item for item in snapshot.checkpoints}
    models = {item.model_id: item for item in snapshot.models}
    rows: list[dict[str, Any]] = []
    manual: list[dict[str, Any]] = []
    evidence_index: list[dict[str, Any]] = []
    for checkpoint_id, plan in plan_rows.items():
        if plan["download_status"] != "license_review_required":
            continue
        checkpoint = checkpoints[checkpoint_id]
        model = models[checkpoint.model_id]
        provenance = provenance_rows[checkpoint_id]
        config = evidence_config["models"][checkpoint.model_id]
        project_url = config.get("official_project_url") or model.code_url
        readme_url = project_readme_url(project_url)
        license_url = config.get("license_url")
        project_evidence = fetch_evidence(session, readme_url)
        license_evidence = fetch_evidence(session, raw_license_url(license_url))
        access_reachable = plan["access_status"] in {
            "accessible_source_unverified",
            "verified_accessible",
        }
        status, code_status, weight_status, reason = classify_license(
            code_evidence=license_evidence,
            registered_status=provenance["license_status"],
            weight_reachable=access_reachable,
        )
        checked_at = datetime.now(timezone.utc).isoformat()
        summary = sanitize_text(config.get("evidence_summary", ""))
        row = {
            "model_id": checkpoint.model_id,
            "checkpoint_id": checkpoint_id,
            "checkpoint_name": checkpoint.checkpoint_name,
            "official_project_url": project_url,
            "official_code_url": model.code_url,
            "license_url": license_url or "",
            "weight_entry_url": checkpoint.weight_url or "",
            "registered_license_status": provenance["license_status"],
            "code_license_status": code_status,
            "weight_license_status": weight_status,
            "license_status": status,
            "license_confidence": "high"
            if status == "license_verified"
            else "medium"
            if project_evidence["reachable"]
            else "low",
            "evidence_summary": summary,
            "code_evidence_reachable": project_evidence["reachable"],
            "license_evidence_reachable": license_evidence["reachable"],
            "weight_entry_reachable": access_reachable,
            "weight_entry_status": plan["access_status"],
            "manual_review_reason": reason,
            "checked_at": checked_at,
        }
        rows.append(row)
        manual.append(
            {
                "checkpoint_id": checkpoint_id,
                "current_blocker": reason,
                "required_user_action": (
                    "确认代码许可证是否覆盖权重文件，并确认当前研究用途符合权重许可范围。"
                ),
                "official_entry": project_url,
                "license_url": license_url or "未登记",
                "login_required": plan["download_status"] == "authentication_required",
                "license_acceptance_required": True,
                "next_command": "python scripts/audit_checkpoint_license.py --run-id <new-run-id>",
            }
        )
        evidence_index.append(
            {
                "model_id": checkpoint.model_id,
                "checkpoint_id": checkpoint_id,
                "supporting_urls": [
                    item
                    for item in [
                        project_evidence["url"],
                        license_evidence["url"],
                        checkpoint.weight_url,
                    ]
                    if item
                ],
                "evidence_type": "official_project_readme_license_page_and_weight_entry",
                "fetched_at": checked_at,
                "page_titles": [
                    item["title"] for item in [project_evidence, license_evidence] if item["title"]
                ],
                "evidence_summary": summary,
            }
        )
    return rows, manual, evidence_index


def write_outputs(
    output_dir: Path,
    rows: list[dict[str, Any]],
    manual: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=False)
    for name, payload in [("license_review.csv", rows), ("manual_review.csv", manual)]:
        fields = list(payload[0]) if payload else []
        with (output_dir / name).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(payload)
    (output_dir / "evidence_index.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    counts = Counter(row["license_status"] for row in rows)
    lines = [
        "# Checkpoint 许可证核验",
        "",
        f"- 核验 checkpoint：{len(rows)}",
        *[f"- `{status}`：{count}" for status, count in sorted(counts.items())],
        "- 本轮区分代码许可证与权重许可证，未修改 registry 最终状态。",
    ]
    (output_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--plan",
        type=Path,
        default=Path("artifacts/checkpoint_download/checkpoint_download_plan.csv"),
    )
    parser.add_argument(
        "--provenance",
        type=Path,
        default=Path("audits/checkpoint_provenance/20260713T021231Z/checkpoint_provenance.csv"),
    )
    parser.add_argument(
        "--evidence-config",
        type=Path,
        default=Path("audits/checkpoint_provenance/source_evidence.yaml"),
    )
    parser.add_argument("--output-root", type=Path, default=Path("audits/checkpoint_license"))
    parser.add_argument("--run-id", default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    args = parser.parse_args()
    snapshot = load_registry()
    plan = read_csv(args.plan)
    provenance = read_csv(args.provenance)
    config = yaml.safe_load(args.evidence_config.read_text(encoding="utf-8"))
    with requests.Session() as session:
        rows, manual, evidence = build_rows(
            plan_rows=plan,
            provenance_rows=provenance,
            evidence_config=config,
            snapshot=snapshot,
            session=session,
        )
    write_outputs(args.output_root / args.run_id, rows, manual, evidence)
    print(f"Audited {len(rows)} license records -> {args.output_root / args.run_id}")


if __name__ == "__main__":
    main()
