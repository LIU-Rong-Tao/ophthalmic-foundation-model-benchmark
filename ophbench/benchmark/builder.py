from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml


def _write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_benchmark(release_path: Path, runs_root: Path, output_dir: Path) -> dict:
    """Build deterministic, static dashboard input without reading experiments at render time."""
    release = yaml.safe_load(release_path.read_text(encoding="utf-8")) or {}
    release_id = release.get("release_id")
    if not release_id:
        raise ValueError("release file must define release_id")
    runs = []
    for path in sorted(runs_root.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("release_id") == release_id:
            runs.append(payload)
    output_dir.mkdir(parents=True, exist_ok=True)
    leaderboard = sorted(runs, key=lambda run: run.get("metrics", {}).get("Macro-F1") or -1, reverse=True)
    insights = {
        "metric_comparison": [
            {"model_id": run["model_id"], **run.get("metrics", {}), **run.get("cost", {})}
            for run in leaderboard
        ],
        "stable_class_winners": {},
        "limitations": release.get("limitations", []),
    }
    files = {
        "releases.json": [release],
        "leaderboard.json": leaderboard,
        "insights.json": insights,
        "model_details.json": {run["run_id"]: run for run in runs},
    }
    for name, payload in files.items():
        _write_json(output_dir / name, payload)
    checksums = {name: hashlib.sha256((output_dir / name).read_bytes()).hexdigest() for name in files}
    _write_json(output_dir / "artifact_manifest.json", checksums)
    return {"release_id": release_id, "run_count": len(runs), "output_dir": str(output_dir)}
