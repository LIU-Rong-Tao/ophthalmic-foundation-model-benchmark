import csv
import json
from pathlib import Path

import numpy as np

from ophbench.evaluation import PrecomputedProbeConfig, run_precomputed_probe


def _write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def test_precomputed_probe_uses_aligned_features_and_frozen_test(tmp_path: Path):
    rng = np.random.default_rng(2026)
    labels = np.tile(np.arange(3), 30)
    features = np.column_stack(
        [
            labels,
            labels**2,
            rng.normal(0, 0.03, size=len(labels)),
            np.ones(len(labels)),
        ]
    ).astype("float32")
    feature_path = tmp_path / "features.npy"
    np.save(feature_path, features)
    samples_path = tmp_path / "samples.csv"
    _write_csv(
        samples_path,
        [{"canonical_index": index, "canonical_id": f"id-{index}"} for index in range(90)],
        ["canonical_index", "canonical_id"],
    )
    labels_path = tmp_path / "labels.csv"
    _write_csv(
        labels_path,
        [
            {
                "canonical_index": index,
                "label": int(label),
                "class_name": ("Normal", "NPDR", "PDR")[label],
            }
            for index, label in enumerate(labels)
        ],
        ["canonical_index", "label", "class_name"],
    )
    split_path = tmp_path / "split.csv"
    split_rows = []
    for index in range(90):
        split_rows.append(
            {
                "canonical_index": index,
                "split": "development" if index < 60 else "test",
                "cv_fold": index % 5 if index < 60 else "",
            }
        )
    _write_csv(split_path, split_rows, ["canonical_index", "split", "cv_fold"])
    output = run_precomputed_probe(
        PrecomputedProbeConfig(
            features=feature_path,
            samples=samples_path,
            labels=labels_path,
            split_manifest=split_path,
            output_dir=tmp_path / "output",
            release_id="test-v1",
            model_id="fake",
            checkpoint_id="fake-v1",
            task_id="dr-stage-3class",
            task_display_name="DR stage",
            task_type="ordinal_classification",
            label_semantics="verified_dr_grade",
            qualification_status="public_dataset_holdout",
        )
    )
    metrics = json.loads((output / "metrics.json").read_text(encoding="utf-8"))
    manifest = json.loads((output / "run_manifest.json").read_text(encoding="utf-8"))
    summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
    assert metrics["macro_f1"] > 0.95
    assert metrics["quadratic_weighted_kappa"] > 0.95
    assert metrics["top3_accuracy"] is None
    assert manifest["task_metadata"]["class_count"] == 3
    assert manifest["task_metadata"]["task_type"] == "ordinal_classification"
    assert manifest["task_metadata"]["label_semantics"] == "verified_dr_grade"
    assert manifest["qualification_status"] == "public_dataset_holdout"
    assert manifest["test_used_for_selection"] is False
    assert summary["development_test_disjoint"] is True
    assert (output / "artifact_manifest.json").is_file()
