import json
from pathlib import Path

import yaml

from ophbench.benchmark import build_benchmark
from ophbench.benchmark.builder import _leaderboard_sort_key, _stable_winners
from ophbench.benchmark.metrics import normalize_metrics


def _run(release: str, task: str, model: str, score: float) -> dict:
    return {
        "run_id": f"{release}--{model}--{task}",
        "release_id": release,
        "model_id": model,
        "checkpoint_id": f"{model}-checkpoint",
        "adapter_version": "test",
        "protocol_id": "test",
        "task_id": task,
        "task_metadata": {
            "display_name": task,
            "task_type": "single_label_multiclass_classification",
            "class_count": 3,
        },
        "qualification_status": "exploratory",
        "metrics": {"Macro-F1": score},
        "cost": {},
        "artifacts": {},
        "limitations": [],
        "per_class": [
            {"class_id": 0, "F1": score, "Recall": score, "Support": 8},
            {"class_id": 1, "F1": score, "Recall": score, "Support": 3},
        ],
        "stability": {},
    }


def test_benchmark_builder_groups_leaderboards_and_winners_by_task(tmp_path: Path):
    release = {
        "release_id": "release-v1",
        "default_task_id": "task-a",
        "task_ids": ["task-a", "task-b"],
    }
    release_path = tmp_path / "release.yaml"
    release_path.write_text(yaml.safe_dump(release), encoding="utf-8")
    runs = tmp_path / "runs"
    runs.mkdir()
    for task, model, score in (
        ("task-a", "model-1", 0.8),
        ("task-a", "model-2", 0.6),
        ("task-b", "model-1", 0.4),
        ("task-b", "model-2", 0.9),
    ):
        payload = _run("release-v1", task, model, score)
        (runs / f"{payload['run_id']}.json").write_text(
            json.dumps(payload),
            encoding="utf-8",
        )
    output = tmp_path / "generated"
    build_benchmark(release_path, runs, output)
    insights = json.loads((output / "insights.json").read_text(encoding="utf-8"))
    tasks = json.loads((output / "tasks.json").read_text(encoding="utf-8"))
    assert [item["task_id"] for item in tasks] == ["task-a", "task-b"]
    assert insights["by_task"]["task-a"]["metric_comparison"][0]["model_id"] == "model-1"
    assert insights["by_task"]["task-b"]["metric_comparison"][0]["model_id"] == "model-2"
    assert insights["by_task"]["task-a"]["stable_class_winners"]["F1"] == {"model-1": 1}
    assert insights["by_task"]["task-a"]["stable_class_count"] == 1
    assert insights["by_task"]["task-a"]["stable_class_tie_policy"] == "co_winners_counted"


def test_stable_winners_count_exact_ties_for_every_co_winner():
    runs = [
        {
            "model_id": model_id,
            "per_class": [{"class_id": 0, "F1": 0.8, "Recall": 0.7, "Support": 8}],
        }
        for model_id in ("model-1", "model-2")
    ]

    assert _stable_winners(runs)["F1"] == {"model-1": 1, "model-2": 1}


def test_metric_aliases_and_zero_score_sorting_are_canonical():
    assert normalize_metrics(
        {
            "macro_auprc": 0.71,
            "average_precision": 0.62,
        }
    ) == {
        "Macro-AUPRC": 0.71,
        "AUPRC": 0.62,
    }
    runs = [
        {"task_id": "task", "model_id": "missing", "metrics": {}},
        {"task_id": "task", "model_id": "zero", "metrics": {"Macro-F1": 0.0}},
    ]
    assert sorted(runs, key=_leaderboard_sort_key)[0]["model_id"] == "zero"
