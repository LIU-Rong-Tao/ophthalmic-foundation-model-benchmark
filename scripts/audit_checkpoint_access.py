#!/usr/bin/env python3
"""Audit registered checkpoint access without downloading full model weights."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import requests

from ophbench import load_registry

PROBE_BYTES = 1024
DOWNLOADABLE = {"verified_accessible"}
MODEL_EXTENSIONS = (".safetensors", ".pth", ".pt", ".bin", ".ckpt", ".zip")


@dataclass
class AuditRow:
    model_id: str
    checkpoint_id: str
    checkpoint_name: str
    declared_url: str | None
    resolved_url: str | None
    provider: str
    official_source_status: str
    access_status: str
    authentication_required: bool
    server_accessible: bool
    actual_filename: str | None
    size_bytes: int | None
    content_type: str | None
    probe_result: str
    failure_reason: str | None
    checked_at: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def google_drive_file_id(url: str | None) -> str | None:
    if not url:
        return None
    match = re.search(r"/file/d/([^/]+)", url)
    if match:
        return match.group(1)
    return parse_qs(urlparse(url).query).get("id", [None])[0]


def _filename(headers: dict[str, str]) -> str | None:
    disposition = headers.get("content-disposition", "")
    match = re.search(r"filename\*?=(?:UTF-8''|\")?([^;\"]+)", disposition, re.I)
    return match.group(1).strip() if match else None


def _size(headers: dict[str, str]) -> int | None:
    content_range = headers.get("content-range", "")
    match = re.search(r"/(\d+)$", content_range)
    if match:
        return int(match.group(1))
    try:
        return int(headers["content-length"])
    except (KeyError, ValueError):
        return None


def _registry_source_status(checkpoint: Any) -> str:
    verification = getattr(checkpoint, "verification", None)
    if verification and getattr(verification, "checkpoint_url", "pending") == "verified":
        return "verified_registry_evidence"
    return "source_unverified"


def _base_row(checkpoint: Any) -> AuditRow:
    return AuditRow(
        model_id=str(checkpoint.model_id),
        checkpoint_id=str(checkpoint.checkpoint_id),
        checkpoint_name=str(checkpoint.checkpoint_name),
        declared_url=checkpoint.weight_url,
        resolved_url=None,
        provider=str(checkpoint.provider),
        official_source_status=_registry_source_status(checkpoint),
        access_status="not_checked",
        authentication_required=bool(checkpoint.requires_auth),
        server_accessible=False,
        actual_filename=None,
        size_bytes=None,
        content_type=None,
        probe_result="not_run",
        failure_reason=None,
        checked_at=utc_now(),
    )


def _request_probe(
    url: str,
    *,
    session: requests.Session,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    request_headers = {"Range": f"bytes=0-{PROBE_BYTES - 1}"}
    if headers:
        request_headers.update(headers)
    for attempt in range(3):
        response = None
        try:
            response = session.get(
                url,
                headers=request_headers,
                allow_redirects=True,
                stream=True,
                timeout=(10, 30),
            )
            response_headers = {key.lower(): value for key, value in response.headers.items()}
            sample = next(response.iter_content(chunk_size=PROBE_BYTES), b"")
            return {
                "status": response.status_code,
                "url": response.url,
                "headers": response_headers,
                "sample": sample,
            }
        except requests.RequestException:
            if attempt == 2:
                raise
            time.sleep(attempt + 1)
        finally:
            if response is not None:
                response.close()
    raise RuntimeError("unreachable")


def _probe_huggingface(row: AuditRow, *, token: str | None, session: requests.Session) -> AuditRow:
    try:
        from huggingface_hub import HfApi
        from huggingface_hub.errors import GatedRepoError, HfHubHTTPError, RepositoryNotFoundError
    except ImportError:
        row.access_status = "manual_review_required"
        row.failure_reason = "huggingface_hub is not installed"
        return row
    parsed = urlparse(row.declared_url or "")
    parts = [item for item in parsed.path.split("/") if item]
    if len(parts) < 2:
        row.access_status = "manual_review_required"
        row.failure_reason = "Hugging Face repo identifier cannot be parsed"
        return row
    repo_id = "/".join(parts[:2])
    try:
        info = HfApi(token=token).repo_info(repo_id, files_metadata=True, token=token)
        files = [
            item for item in info.siblings if item.rfilename.lower().endswith(MODEL_EXTENSIONS)
        ]
        if not files:
            row.access_status = "official_file_missing"
            row.failure_reason = "No checkpoint-like file listed in repository metadata"
            return row
        largest = max(files, key=lambda item: item.size or 0)
        row.resolved_url = f"https://huggingface.co/{repo_id}/resolve/main/{largest.rfilename}"
        row.actual_filename = largest.rfilename
        row.size_bytes = largest.size
        probe_headers = {"Authorization": f"Bearer {token}"} if token else None
        result = _request_probe(row.resolved_url, session=session, headers=probe_headers)
        row.resolved_url = result["url"]
        row.content_type = result["headers"].get("content-type")
        if result["status"] < 400:
            row.size_bytes = _size(result["headers"]) or row.size_bytes
        is_html = "html" in (row.content_type or "").lower() or result[
            "sample"
        ].lstrip().startswith(b"<")
        if result["status"] in {401, 403}:
            row.authentication_required = True
            row.access_status = "authentication_required"
            row.failure_reason = f"Hugging Face HTTP {result['status']} for checkpoint file"
        elif result["status"] >= 400:
            row.access_status = "broken_link"
            row.failure_reason = f"Hugging Face HTTP {result['status']} for checkpoint file"
        elif is_html:
            row.access_status = "manual_review_required"
            row.failure_reason = "Hugging Face returned HTML, not a verifiable checkpoint file"
        else:
            row.server_accessible = True
            row.access_status = (
                "verified_accessible"
                if row.official_source_status == "verified_registry_evidence"
                else "accessible_source_unverified"
            )
            row.probe_result = (
                "repository metadata and checkpoint range probe returned "
                f"{len(result['sample'])} byte(s)"
            )
    except GatedRepoError:
        row.authentication_required = True
        row.access_status = "authentication_required"
        row.failure_reason = "Hugging Face repository is gated for current server credentials"
    except RepositoryNotFoundError:
        row.access_status = "broken_link"
        row.failure_reason = "Hugging Face repository was not found or is private"
    except HfHubHTTPError as exc:
        row.access_status = (
            "authentication_required" if exc.response.status_code in {401, 403} else "probe_failed"
        )
        row.failure_reason = f"Hugging Face HTTP {exc.response.status_code}"
    except Exception as exc:
        row.access_status = "probe_failed"
        row.failure_reason = f"{type(exc).__name__}: {exc}"
    return row


def _probe_zenodo(row: AuditRow, *, session: requests.Session) -> AuditRow:
    record = re.search(r"/records/(\d+)", row.declared_url or "")
    if not record:
        row.access_status = "manual_review_required"
        row.failure_reason = "Zenodo record identifier cannot be parsed"
        return row
    try:
        response = session.get(
            f"https://zenodo.org/api/records/{record.group(1)}", timeout=(10, 30)
        )
        response.raise_for_status()
        files = response.json().get("files", [])
        declared_name = Path(urlparse(row.declared_url or "").path).name
        selected = next((item for item in files if item.get("key") == declared_name), None)
        if not selected:
            row.access_status = "official_file_missing"
            row.failure_reason = "Declared file is absent from Zenodo record"
            return row
        row.resolved_url = selected.get("links", {}).get("self")
        row.actual_filename = selected.get("key")
        row.size_bytes = selected.get("size")
        row.content_type = "repository_metadata"
        row.server_accessible = True
        row.access_status = "accessible_source_unverified"
        row.probe_result = "Zenodo record lists declared file"
    except requests.RequestException as exc:
        row.access_status = "probe_failed"
        row.failure_reason = f"{type(exc).__name__}: {exc}"
    return row


def _probe_github_release(row: AuditRow, *, session: requests.Session) -> AuditRow:
    match = re.search(r"github\.com/([^/]+)/([^/]+)/releases/tag/([^/?#]+)", row.declared_url or "")
    if not match:
        row.access_status = "manual_review_required"
        row.failure_reason = "GitHub release tag URL cannot be parsed"
        return row
    owner, repo, tag = match.groups()
    headers = {"Accept": "application/vnd.github+json"}
    if os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    try:
        response = session.get(
            f"https://api.github.com/repos/{owner}/{repo}/releases/tags/{tag}",
            headers=headers,
            timeout=(10, 30),
        )
        if response.status_code == 404:
            row.access_status = "official_file_missing"
            row.failure_reason = "GitHub release tag or release assets were not found"
            return row
        response.raise_for_status()
        assets = response.json().get("assets", [])
        if not assets:
            row.access_status = "official_file_missing"
            row.failure_reason = "GitHub release contains no downloadable assets"
            return row
        selected = max(assets, key=lambda item: item.get("size", 0))
        row.resolved_url = selected.get("browser_download_url")
        row.actual_filename = selected.get("name")
        row.size_bytes = selected.get("size")
        row.content_type = "release_metadata"
        row.server_accessible = True
        row.access_status = "accessible_source_unverified"
        row.probe_result = f"GitHub release {tag} lists {len(assets)} asset(s)"
    except requests.RequestException as exc:
        row.access_status = "probe_failed"
        row.failure_reason = f"{type(exc).__name__}: {exc}"
    return row


def _probe_google_drive(row: AuditRow, *, session: requests.Session) -> AuditRow:
    file_id = google_drive_file_id(row.declared_url)
    if not file_id:
        row.access_status = "manual_review_required"
        row.failure_reason = "Google Drive file identifier cannot be parsed"
        return row
    try:
        result = _request_probe(
            f"https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm=t",
            session=session,
        )
        row.resolved_url = result["url"]
        row.content_type = result["headers"].get("content-type")
        row.actual_filename = _filename(result["headers"])
        row.size_bytes = _size(result["headers"])
        is_html = "html" in (row.content_type or "").lower() or result[
            "sample"
        ].lstrip().startswith(b"<")
        if result["status"] in {401, 403}:
            row.authentication_required = True
            row.access_status = "authentication_required"
            row.failure_reason = f"Google Drive HTTP {result['status']}"
        elif result["status"] >= 400:
            row.access_status = "broken_link"
            row.failure_reason = f"Google Drive HTTP {result['status']}"
        elif is_html or not row.actual_filename:
            row.access_status = "manual_review_required"
            row.failure_reason = (
                "Google Drive returned an HTML/confirmation response, not a verifiable file"
            )
        else:
            row.server_accessible = True
            row.access_status = "accessible_source_unverified"
            row.probe_result = f"range probe returned {len(result['sample'])} byte(s)"
    except requests.RequestException as exc:
        row.access_status = "probe_failed"
        row.failure_reason = f"{type(exc).__name__}: {exc}"
    return row


def audit_checkpoint(
    checkpoint: Any, *, session: requests.Session, hf_token: str | None
) -> AuditRow:
    row = _base_row(checkpoint)
    if not row.declared_url:
        row.access_status = "official_file_missing"
        row.failure_reason = "No declared weight URL"
    elif row.provider == "huggingface":
        row = _probe_huggingface(row, token=hf_token, session=session)
    elif row.provider == "zenodo":
        row = _probe_zenodo(row, session=session)
    elif row.provider == "github_release":
        row = _probe_github_release(row, session=session)
    elif row.provider == "google_drive":
        row = _probe_google_drive(row, session=session)
    else:
        row.access_status = "manual_review_required"
        row.failure_reason = f"No safe probe implementation for provider={row.provider}"
    return row


def build_download_plan(rows: list[AuditRow], *, cache_root: Path) -> list[dict[str, Any]]:
    plan = []
    for row in rows:
        downloadable = row.access_status in DOWNLOADABLE and row.server_accessible
        plan.append(
            {
                "model_id": row.model_id,
                "checkpoint_id": row.checkpoint_id,
                "actual_filename": row.actual_filename or "",
                "estimated_size_bytes": row.size_bytes,
                "access_status": row.access_status,
                "downloadable_now": downloadable,
                "manual_action_required": not downloadable,
                "recommended_local_path": str(
                    cache_root / row.model_id / row.checkpoint_id / (row.actual_filename or "")
                ),
            }
        )
    return plan


def write_report(rows: list[AuditRow], *, output_dir: Path, cache_root: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = [asdict(row) for row in rows]
    fields = list(payload[0]) if payload else list(AuditRow.__annotations__)
    with (output_dir / "checkpoint_access_audit.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(payload)
    (output_dir / "checkpoint_access_audit.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    plan = build_download_plan(rows, cache_root=cache_root)
    with (output_dir / "download_plan.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(plan[0]) if plan else [])
        writer.writeheader()
        writer.writerows(plan)
    counts: dict[str, int] = {}
    for row in rows:
        counts[row.access_status] = counts.get(row.access_status, 0) + 1
    known_bytes = sum(row.size_bytes or 0 for row in rows if row.server_accessible)
    free_bytes = shutil.disk_usage(
        cache_root.parent if cache_root.parent.exists() else Path("/")
    ).free
    summary = ["# Checkpoint 权重可获取性审计", "", f"- 总 checkpoint：{len(rows)}"]
    summary.extend(f"- `{status}`：{count}" for status, count in sorted(counts.items()))
    summary.extend(
        [
            f"- 已知可访问资产总体积：{known_bytes / 1024**3:.2f} GB",
            f"- 缓存所在文件系统剩余空间：{free_bytes / 1024**3:.2f} GB",
            "- 本报告仅做元数据和小字节 probe，未下载完整权重。",
        ]
    )
    (output_dir / "summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir", type=Path, default=Path("artifacts/checkpoint_access_audit")
    )
    parser.add_argument("--cache-root", type=Path, default=Path("/data/LRT/model_cache/ophbench"))
    args = parser.parse_args()
    snapshot = load_registry()
    session = requests.Session()
    rows = [
        audit_checkpoint(item, session=session, hf_token=os.getenv("HF_TOKEN"))
        for item in snapshot.checkpoints
    ]
    if len(rows) != snapshot.checkpoint_count:
        raise RuntimeError("Audit did not produce one row for every registered checkpoint")
    write_report(rows, output_dir=args.output_dir, cache_root=args.cache_root)
    print(f"Audited {len(rows)} checkpoints -> {args.output_dir}")


if __name__ == "__main__":
    main()
