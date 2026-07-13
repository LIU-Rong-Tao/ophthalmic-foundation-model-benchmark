#!/usr/bin/env python3
"""Download one approved checkpoint with resume and SHA256 verification."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlparse, urlunparse

import requests

from ophbench import load_registry

MANIFEST_FIELDS = [
    "model_id",
    "checkpoint_id",
    "provider",
    "source_url",
    "resolved_url",
    "filename",
    "local_path",
    "size_bytes",
    "sha256",
    "downloaded_at",
    "license_status",
    "verification_status",
    "source_revision",
]
SECRET_QUERY_KEYS = {
    "token",
    "access_token",
    "auth",
    "authorization",
    "cookie",
    "signature",
    "sig",
    "jwt",
    "policy",
    "sp",
    "ske",
    "skt",
    "se",
    "sv",
}


def read_rows(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return {row["checkpoint_id"]: row for row in csv.DictReader(handle)}


def sanitize_url(value: str | None) -> str:
    if not value:
        return ""
    parsed = urlparse(value)
    if (
        parsed.netloc.lower().endswith("cdn.hf.co")
        or parsed.netloc.lower() == "release-assets.githubusercontent.com"
    ):
        return urlunparse(parsed._replace(query=""))
    query = []
    for item in parsed.query.split("&"):
        if not item:
            continue
        key = item.split("=", 1)[0].lower()
        query.append(f"{key}=[REDACTED]" if key in SECRET_QUERY_KEYS else item)
    return urlunparse(parsed._replace(query="&".join(query)))


def source_url(plan: dict[str, str], access: dict[str, str]) -> str:
    if plan["provider"] == "huggingface":
        repo = plan["registered_weight_url"].rstrip("/")
        return f"{repo}/resolve/main/{quote(plan['actual_filename'])}"
    return access.get("resolved_url") or plan["registered_weight_url"]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(path: Path, record: dict[str, str]) -> None:
    rows = read_rows(path) if path.exists() else {}
    rows[record["checkpoint_id"]] = record
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows.values())


def download_one(
    *,
    plan: dict[str, str],
    access: dict[str, str],
    checkpoint: object,
    cache_root: Path,
    manifest_path: Path,
    token: str | None,
) -> dict[str, str]:
    if plan["download_status"] != "ready_to_download":
        raise ValueError(f"checkpoint is not ready_to_download: {plan['download_status']}")
    filename = plan["actual_filename"]
    if not filename or "/" in filename or "\\" in filename:
        raise ValueError("checkpoint filename is missing or unsafe")
    destination = cache_root / plan["model_id"] / plan["checkpoint_id"] / filename
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_name(destination.name + ".part")
    expected_size = int(plan["estimated_size_bytes"]) if plan["estimated_size_bytes"] else None
    expected_sha = getattr(checkpoint, "sha256", None)
    existing_manifest = (
        read_rows(manifest_path).get(plan["checkpoint_id"], {}) if manifest_path.exists() else {}
    )
    if destination.exists():
        actual_sha = sha256_file(destination)
        known_sha = expected_sha or existing_manifest.get("sha256")
        if known_sha and actual_sha == known_sha:
            record = {
                "model_id": plan["model_id"],
                "checkpoint_id": plan["checkpoint_id"],
                "provider": plan["provider"],
                "source_url": plan["registered_weight_url"],
                "resolved_url": sanitize_url(existing_manifest.get("resolved_url", "")),
                "filename": filename,
                "local_path": str(destination),
                "size_bytes": str(destination.stat().st_size),
                "sha256": actual_sha,
                "downloaded_at": existing_manifest.get(
                    "downloaded_at", datetime.now(timezone.utc).isoformat()
                ),
                "license_status": plan["license_status"],
                "verification_status": "sha256_match_skipped",
                "source_revision": existing_manifest.get("source_revision", ""),
            }
            write_manifest(manifest_path, record)
            return record
        raise FileExistsError("destination exists but no matching SHA256 is recorded")

    url = source_url(plan, access)
    headers = (
        {"Authorization": f"Bearer {token}"} if token and plan["provider"] == "huggingface" else {}
    )
    offset = partial.stat().st_size if partial.exists() else 0
    if expected_size is not None and offset > expected_size:
        raise ValueError("partial file is larger than registered size")
    if offset:
        headers["Range"] = f"bytes={offset}-"
    try:
        with requests.get(
            url, headers=headers, stream=True, allow_redirects=True, timeout=(20, 120)
        ) as response:
            if response.status_code in {401, 403}:
                raise PermissionError("checkpoint server requires authentication or approval")
            response.raise_for_status()
            iterator = response.iter_content(chunk_size=1024 * 1024)
            first = next(iterator, b"")
            content_type = response.headers.get("content-type", "")
            if "html" in content_type.lower() or re.match(rb"\s*<", first):
                raise ValueError("download response is HTML, not a checkpoint file")
            append = bool(offset and response.status_code == 206)
            if offset and not append:
                offset = 0
            with partial.open("ab" if append else "wb") as handle:
                handle.write(first)
                for chunk in iterator:
                    if chunk:
                        handle.write(chunk)
            resolved_url = sanitize_url(response.url)
            source_revision = response.headers.get("x-repo-commit", "")
    except Exception:
        raise

    actual_size = partial.stat().st_size
    if expected_size is not None and actual_size != expected_size:
        raise ValueError(f"download size mismatch: got {actual_size}, expected {expected_size}")
    digest = sha256_file(partial)
    if expected_sha and digest != expected_sha:
        raise ValueError("download SHA256 does not match registry")
    partial.replace(destination)
    record = {
        "model_id": plan["model_id"],
        "checkpoint_id": plan["checkpoint_id"],
        "provider": plan["provider"],
        "source_url": plan["registered_weight_url"],
        "resolved_url": resolved_url,
        "filename": filename,
        "local_path": str(destination),
        "size_bytes": str(actual_size),
        "sha256": digest,
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "license_status": plan["license_status"],
        "verification_status": "downloaded_sha256_checked",
        "source_revision": source_revision,
    }
    write_manifest(manifest_path, record)
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint-id", required=True)
    parser.add_argument(
        "--plan",
        type=Path,
        default=Path("artifacts/checkpoint_download/checkpoint_download_plan.csv"),
    )
    parser.add_argument(
        "--access-audit",
        type=Path,
        default=Path("artifacts/checkpoint_access_audit/checkpoint_access_audit.csv"),
    )
    parser.add_argument("--cache-root", type=Path, default=Path("/data/LRT/model_cache/ophbench"))
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    plan = read_rows(args.plan)[args.checkpoint_id]
    access = read_rows(args.access_audit)[args.checkpoint_id]
    snapshot = load_registry()
    checkpoint = next(
        item for item in snapshot.checkpoints if item.checkpoint_id == args.checkpoint_id
    )
    manifest = args.manifest or args.cache_root / "local_asset_manifest.csv"
    record = download_one(
        plan=plan,
        access=access,
        checkpoint=checkpoint,
        cache_root=args.cache_root,
        manifest_path=manifest,
        token=None if plan["provider"] != "huggingface" else __import__("os").getenv("HF_TOKEN"),
    )
    print(
        f"{record['checkpoint_id']}: {record['verification_status']} "
        f"{record['size_bytes']} bytes sha256={record['sha256']}"
    )


if __name__ == "__main__":
    main()
