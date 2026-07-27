from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

from .metrics import SINGLE_LABEL_HOME_METRICS


def _write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _stable_winners(runs: list[dict]) -> dict[str, dict[str, int]]:
    winners = {metric: {} for metric in ("F1", "Recall", "AUROC")}
    grouped: dict[str, list[tuple[dict, dict]]] = {}
    for run in runs:
        for row in run.get("per_class", []):
            if (row.get("Support") or 0) >= 5:
                key = str(row.get("class_id") or row.get("class_name") or "")
                if key:
                    grouped.setdefault(key, []).append((run, row))
    for candidates in grouped.values():
        for metric in winners:
            available = [(run, row.get(metric)) for run, row in candidates if isinstance(row.get(metric), (int, float))]
            if available:
                winner = max(available, key=lambda item: item[1])[0]["model_id"]
                winners[metric][winner] = winners[metric].get(winner, 0) + 1
    return winners


def _radar_rows(runs: list[dict]) -> list[dict]:
    keys = ("Macro-F1", "Balanced Accuracy", "Accuracy", "Macro-AUROC")
    rows = []
    for run in runs:
        metrics = run.get("metrics", {})
        row = {"model_id": run["model_id"], **{key: metrics.get(key) for key in keys}}
        stability = run.get("stability", {}).get("macro_f1_std")
        row["Stability"] = None if stability is None else max(0.0, 1.0 - float(stability))
        throughput = run.get("cost", {}).get("throughput")
        row["Efficiency"] = throughput
        rows.append(row)
    for key in (*keys, "Efficiency"):
        values = [row[key] for row in rows if isinstance(row.get(key), (int, float))]
        if values:
            minimum, maximum = min(values), max(values)
            for row in rows:
                value = row.get(key)
                row[key] = None if value is None else (1.0 if maximum == minimum else (value - minimum) / (maximum - minimum))
    return rows


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
        "stable_class_winners": _stable_winners(leaderboard),
        "cost_ranking": sorted(
            [run for run in leaderboard if run.get("cost", {}).get("latency_ms") is not None],
            key=lambda run: run["cost"]["latency_ms"],
        ),
        "radar": _radar_rows(leaderboard),
        "home_metrics": list(SINGLE_LABEL_HOME_METRICS),
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
