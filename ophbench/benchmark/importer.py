from __future__ import annotations

import csv
import json
from pathlib import Path

from .metrics import normalize_metrics
from .schemas import ModelRun


def _load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return payload


def _safe_artifact(path: Path) -> str:
    """Only retain a basename so generated dashboard data cannot leak server paths."""
    return path.name


def import_benchmark_run(
    *,
    release_id: str,
    model_id: str,
    task_id: str,
    metrics_path: Path,
    per_class_path: Path | None,
    run_manifest_path: Path | None,
    runs_root: Path,
) -> Path:
    metrics = _load_json(metrics_path)
    manifest = _load_json(run_manifest_path) if run_manifest_path else {}
    normalized_metrics = normalize_metrics(metrics)
    per_class = []
    if per_class_path:
        with per_class_path.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                per_class.append(normalize_metrics(row))
    raw_task = manifest.get("task_metadata") or {}
    task_metadata = {
        key: raw_task.get(key)
        for key in (
            "display_name",
            "task_type",
            "class_count",
            "sample_count",
            "label_space",
            "label_semantics",
        )
        if raw_task.get(key) is not None
    }
    run = ModelRun(
        run_id=f"{release_id}--{model_id}--{task_id}",
        release_id=release_id,
        model_id=model_id,
        checkpoint_id=str(manifest.get("checkpoint_id") or "unknown"),
        adapter_version=manifest.get("adapter_version"),
        protocol_id=str(manifest.get("protocol_id") or "frozen-feature-transfer"),
        task_id=task_id,
        task_metadata=task_metadata,
        qualification_status=str(manifest.get("qualification_status") or "exploratory"),
        metrics=normalized_metrics,
        cost={
            key: manifest.get(key)
            for key in ("throughput", "latency_ms", "peak_vram_gb", "feature_dim")
        },
        artifacts={
            "metrics": _safe_artifact(metrics_path),
            **({"per_class": _safe_artifact(per_class_path)} if per_class_path else {}),
        },
        limitations=list(manifest.get("limitations") or []),
    ).to_dict()
    run["per_class"] = per_class
    run["confusion_matrix"] = manifest.get("confusion_matrix")
    run["stability"] = manifest.get("stability") or {}
    runs_root.mkdir(parents=True, exist_ok=True)
    output = runs_root / f"{run['run_id']}.json"
    output.write_text(
        json.dumps(run, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return output
