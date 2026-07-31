from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

from .metrics import SINGLE_LABEL_HOME_METRICS


def _write_json(path: Path, payload) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _stable_groups(runs: list[dict]) -> dict[str, list[tuple[dict, dict]]]:
    grouped: dict[str, list[tuple[dict, dict]]] = {}
    for run in runs:
        for row in run.get("per_class", []):
            if (row.get("Support") or 0) < 5:
                continue
            class_id = row.get("class_id")
            key = str(class_id if class_id is not None else row.get("class_name") or "")
            if key:
                grouped.setdefault(key, []).append((run, row))
    return grouped


def _stable_winners(runs: list[dict]) -> dict[str, dict[str, int]]:
    winners = {metric: {} for metric in ("F1", "Recall", "AUROC")}
    for candidates in _stable_groups(runs).values():
        for metric in winners:
            available = [
                (run, row.get(metric))
                for run, row in candidates
                if isinstance(row.get(metric), (int, float))
            ]
            if available:
                best = max(float(item[1]) for item in available)
                tied = [
                    run["model_id"]
                    for run, value in available
                    if abs(float(value) - best) <= 1e-12
                ]
                for model_id in tied:
                    winners[metric][model_id] = winners[metric].get(model_id, 0) + 1
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
                row[key] = (
                    None
                    if value is None
                    else (1.0 if maximum == minimum else (value - minimum) / (maximum - minimum))
                )
    return rows


def _task_insights(runs: list[dict], limitations: list[str]) -> dict:
    return {
        "metric_comparison": [
            {"model_id": run["model_id"], **run.get("metrics", {}), **run.get("cost", {})}
            for run in runs
        ],
        "stable_class_winners": _stable_winners(runs),
        "stable_class_count": len(_stable_groups(runs)),
        "stable_class_tie_policy": "co_winners_counted",
        "cost_ranking": sorted(
            [run for run in runs if run.get("cost", {}).get("latency_ms") is not None],
            key=lambda run: run["cost"]["latency_ms"],
        ),
        "radar": _radar_rows(runs),
        "home_metrics": list(SINGLE_LABEL_HOME_METRICS),
        "limitations": limitations,
    }


def _task_catalog(release: dict, runs: list[dict]) -> list[dict]:
    declared = {
        str(task["task_id"]): dict(task)
        for task in release.get("tasks", [])
        if isinstance(task, dict) and task.get("task_id")
    }
    task_ids = list(release.get("task_ids") or [])
    task_ids.extend(
        run["task_id"] for run in runs if run.get("task_id") and run["task_id"] not in task_ids
    )
    catalog = []
    for task_id in task_ids:
        metadata = declared.get(task_id, {"task_id": task_id})
        task_runs = [run for run in runs if run.get("task_id") == task_id]
        if task_runs:
            imported = task_runs[0].get("task_metadata") or {}
            for key, value in imported.items():
                metadata.setdefault(key, value)
        metadata["model_count"] = len(task_runs)
        catalog.append(metadata)
    return catalog


def _leaderboard_sort_key(run: dict) -> tuple[str, float, str]:
    score = run.get("metrics", {}).get("Macro-F1")
    score_order = -float(score) if isinstance(score, (int, float)) else float("inf")
    return (
        str(run.get("task_id") or ""),
        score_order,
        str(run.get("model_id") or ""),
    )


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
    leaderboard = sorted(runs, key=_leaderboard_sort_key)
    tasks = _task_catalog(release, leaderboard)
    default_task_id = str(release.get("default_task_id") or (tasks[0]["task_id"] if tasks else ""))
    by_task = {}
    for task in tasks:
        task_id = str(task["task_id"])
        task_runs = [run for run in leaderboard if run.get("task_id") == task_id]
        by_task[task_id] = _task_insights(
            task_runs,
            list(task.get("limitations") or release.get("limitations", [])),
        )
    insights = {
        "default_task_id": default_task_id,
        "by_task": by_task,
        **(
            by_task[default_task_id]
            if default_task_id in by_task
            else _task_insights([], list(release.get("limitations", [])))
        ),
    }
    files = {
        "releases.json": [release],
        "tasks.json": tasks,
        "leaderboard.json": leaderboard,
        "insights.json": insights,
        "model_details.json": {run["run_id"]: run for run in runs},
    }
    for name, payload in files.items():
        _write_json(output_dir / name, payload)
    checksums = {
        name: hashlib.sha256((output_dir / name).read_bytes()).hexdigest() for name in files
    }
    _write_json(output_dir / "artifact_manifest.json", checksums)
    return {"release_id": release_id, "run_count": len(runs), "output_dir": str(output_dir)}
