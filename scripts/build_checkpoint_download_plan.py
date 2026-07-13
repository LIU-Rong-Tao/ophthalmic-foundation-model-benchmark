#!/usr/bin/env python3
"""Merge access/provenance audits into a conservative checkpoint download plan."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ophbench import load_registry

DOWNLOAD_STATUSES = {
    "ready_to_download",
    "authentication_required",
    "license_review_required",
    "probe_retry_required",
    "not_downloadable",
}
ACCEPTED_LICENSES = {
    "apache-2.0_code_and_weights_declared",
    "cc-by-4.0_models_and_code_declared",
}


def read_csv(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return {row["checkpoint_id"]: row for row in csv.DictReader(handle)}


def latest_provenance_file(root: Path) -> Path:
    candidates = sorted(root.glob("*/checkpoint_provenance.csv"))
    if not candidates:
        raise FileNotFoundError(f"No provenance audit found under {root}")
    return candidates[-1]


def parse_size(value: str | None) -> int | None:
    if value in {None, "", "None", "null"}:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def append_reason(reasons: list[str], value: str | None) -> None:
    if value and value not in reasons:
        reasons.append(value)


def classify(
    *,
    access_status: str,
    provenance_status: str,
    license_status: str,
    size_bytes: int | None,
    registered_url: str | None,
) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if access_status == "authentication_required" or provenance_status == "authentication_required":
        append_reason(reasons, "官方来源已确认，但服务器当前没有权重访问授权。")
        return "authentication_required", reasons
    if access_status in {"probe_failed", "manual_review_required"}:
        append_reason(reasons, "当前访问探测未形成可下载结论，需要重新探测。")
        return "probe_retry_required", reasons
    if not registered_url or provenance_status != "official_source_verified":
        append_reason(reasons, "没有足够的官方来源证据支持下载。")
        return "not_downloadable", reasons
    if size_bytes is None:
        append_reason(reasons, "size_unknown：官方文件大小尚未获取，不能按 0 计算。")
        return "probe_retry_required", reasons
    if license_status not in ACCEPTED_LICENSES:
        append_reason(reasons, "许可证未明确覆盖当前权重获取和研究用途，需要人工确认。")
        return "license_review_required", reasons
    if access_status not in {"accessible_source_unverified", "verified_accessible"}:
        append_reason(reasons, f"访问状态为 {access_status}，暂不下载。")
        return "not_downloadable", reasons
    return "ready_to_download", reasons


def directory_size(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        result = subprocess.run(
            ["du", "-sb", str(path)], capture_output=True, text=True, check=True
        )
        return int(result.stdout.split()[0])
    except (OSError, ValueError, subprocess.CalledProcessError, IndexError):
        return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def disk_summary(cache_root: Path, *, ready_bytes: int) -> dict[str, Any]:
    usage = shutil.disk_usage(cache_root)
    existing_bytes = directory_size(cache_root)
    after_ready = usage.free - ready_bytes
    reserved = int(usage.total * 0.20)
    return {
        "filesystem_total_bytes": usage.total,
        "filesystem_free_bytes": usage.free,
        "existing_cache_bytes": existing_bytes,
        "ready_download_bytes": ready_bytes,
        "free_after_ready_download_bytes": after_ready,
        "reserved_20_percent_bytes": reserved,
        "sufficient_after_20_percent_reserve": after_ready >= reserved,
    }


def build_plan(
    *,
    access_rows: dict[str, dict[str, str]],
    provenance_rows: dict[str, dict[str, str]],
    snapshot: Any,
    cache_root: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    checkpoints = {item.checkpoint_id: item for item in snapshot.checkpoints}
    if set(access_rows) != set(checkpoints) or set(provenance_rows) != set(checkpoints):
        raise ValueError("access/provenance audit rows must cover all registry checkpoints")
    plan: list[dict[str, Any]] = []
    for checkpoint_id, checkpoint in checkpoints.items():
        access = access_rows[checkpoint_id]
        provenance = provenance_rows[checkpoint_id]
        size_bytes = parse_size(access.get("size_bytes"))
        filename = access.get("actual_filename") or provenance.get("exact_filename") or ""
        status, reasons = classify(
            access_status=access.get("access_status", ""),
            provenance_status=provenance.get("provenance_status", ""),
            license_status=provenance.get("license_status", ""),
            size_bytes=size_bytes,
            registered_url=checkpoint.weight_url,
        )
        append_reason(reasons, access.get("failure_reason"))
        if not filename:
            append_reason(reasons, "actual_filename_unknown")
        model_id = checkpoint.model_id
        local_dir = cache_root / model_id / checkpoint_id
        plan.append(
            {
                "model_id": model_id,
                "checkpoint_id": checkpoint_id,
                "checkpoint_name": checkpoint.checkpoint_name,
                "provider": checkpoint.provider,
                "registered_weight_url": checkpoint.weight_url or "",
                "official_source_status": provenance.get("provenance_status", ""),
                "access_status": access.get("access_status", ""),
                "license_status": provenance.get("license_status", ""),
                "actual_filename": filename,
                "estimated_size_bytes": size_bytes,
                "size_status": "known" if size_bytes is not None else "size_unknown",
                "download_status": status,
                "manual_action_required": status != "ready_to_download",
                "recommended_local_dir": str(local_dir),
                "recommended_local_file": str(local_dir / filename) if filename else "",
                "failure_reason": " ".join(reasons),
            }
        )
    ready_bytes = sum(
        item["estimated_size_bytes"] or 0
        for item in plan
        if item["download_status"] == "ready_to_download"
    )
    known_bytes = sum(
        item["estimated_size_bytes"] or 0
        for item in plan
        if item["estimated_size_bytes"] is not None
    )
    resources = disk_summary(cache_root, ready_bytes=ready_bytes)
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "checkpoint_count": len(plan),
        "status_counts": dict(sorted(Counter(item["download_status"] for item in plan).items())),
        "known_weight_bytes": known_bytes,
        "known_weight_size_status": "known_only; size_unknown is never treated as zero",
        "ready_download_bytes": ready_bytes,
        "resource_check": resources,
    }
    return plan, summary


def write_outputs(plan: list[dict[str, Any]], summary: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fields = list(plan[0]) if plan else []
    with (output_dir / "checkpoint_download_plan.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(plan)
    (output_dir / "checkpoint_download_plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Checkpoint 下载计划",
        "",
        f"- checkpoint 总数：{summary['checkpoint_count']}",
        f"- 已知权重总体积：{summary['known_weight_bytes'] / 1024**3:.2f} GiB",
        f"- ready_to_download 总体积：{summary['ready_download_bytes'] / 1024**3:.2f} GiB",
        f"- 磁盘剩余空间：{summary['resource_check']['filesystem_free_bytes'] / 1024**3:.2f} GiB",
        "- 预留 20% 后是否足够："
        f"{summary['resource_check']['sufficient_after_20_percent_reserve']}",
        "- 本轮只生成计划，未下载任何权重。",
        "",
        "## 状态数量",
        "",
    ]
    for status, count in summary["status_counts"].items():
        lines.append(f"- `{status}`：{count}")
    for status in sorted(DOWNLOAD_STATUSES):
        lines.extend(["", f"## {status}", ""])
        selected = [item for item in plan if item["download_status"] == status]
        if not selected:
            lines.append("无。")
        for item in selected:
            size = (
                f"{item['estimated_size_bytes'] / 1024**3:.2f} GiB"
                if item["estimated_size_bytes"] is not None
                else "size_unknown"
            )
            lines.append(
                f"- `{item['checkpoint_id']}`：{size}；{item['failure_reason'] or '可进入下载验证'}"
            )
    (output_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--access-audit",
        type=Path,
        default=Path("artifacts/checkpoint_access_audit/checkpoint_access_audit.csv"),
    )
    parser.add_argument("--provenance-audit", type=Path)
    parser.add_argument(
        "--provenance-root", type=Path, default=Path("audits/checkpoint_provenance")
    )
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/checkpoint_download"))
    parser.add_argument("--cache-root", type=Path, default=Path("/data/LRT/model_cache"))
    args = parser.parse_args()
    provenance_path = args.provenance_audit or latest_provenance_file(args.provenance_root)
    access_rows = read_csv(args.access_audit)
    provenance_rows = read_csv(provenance_path)
    snapshot = load_registry()
    plan, summary = build_plan(
        access_rows=access_rows,
        provenance_rows=provenance_rows,
        snapshot=snapshot,
        cache_root=args.cache_root,
    )
    write_outputs(plan, summary, args.output_dir)
    print(f"Generated {len(plan)} checkpoint download records -> {args.output_dir}")


if __name__ == "__main__":
    main()
