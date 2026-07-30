from __future__ import annotations

import csv
import hashlib
import json
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass(frozen=True)
class PrecomputedProbeConfig:
    features: Path
    samples: Path
    labels: Path
    split_manifest: Path
    output_dir: Path
    release_id: str
    model_id: str
    checkpoint_id: str
    task_id: str
    adapter_version: str | None = None
    seed: int = 2026
    c_candidates: tuple[float, ...] = (0.01, 0.1, 1.0, 10.0)
    task_display_name: str | None = None
    label_space: str | None = None
    limitations: tuple[str, ...] = (
        "Image-level split; patient identifiers are unavailable.",
        "Observed directory labels are exploratory and may not capture hidden comorbidity.",
    )


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _top_k_accuracy(labels: np.ndarray, probabilities: np.ndarray, k: int) -> float | None:
    if probabilities.shape[1] <= k:
        return None
    top = np.argpartition(probabilities, -k, axis=1)[:, -k:]
    return float(np.mean(np.any(top == labels[:, None], axis=1)))


def _metrics(
    labels: np.ndarray,
    probabilities: np.ndarray,
    class_ids: np.ndarray,
) -> tuple[dict[str, float | None], np.ndarray, list[dict[str, Any]]]:
    from sklearn.metrics import (
        accuracy_score,
        average_precision_score,
        balanced_accuracy_score,
        confusion_matrix,
        f1_score,
        precision_recall_fscore_support,
        roc_auc_score,
    )
    from sklearn.preprocessing import label_binarize

    predictions = probabilities.argmax(axis=1)
    matrix = confusion_matrix(labels, predictions, labels=class_ids)
    precision, recall, f1, support = precision_recall_fscore_support(
        labels,
        predictions,
        labels=class_ids,
        zero_division=0,
    )
    binary = label_binarize(labels, classes=class_ids)
    if binary.shape[1] == 1:
        binary = np.column_stack([1 - binary[:, 0], binary[:, 0]])
    per_class = []
    aurocs: list[float] = []
    auprcs: list[float] = []
    total = int(matrix.sum())
    for offset, class_id in enumerate(class_ids):
        true_positive = int(matrix[offset, offset])
        false_positive = int(matrix[:, offset].sum() - true_positive)
        false_negative = int(matrix[offset, :].sum() - true_positive)
        true_negative = total - true_positive - false_positive - false_negative
        denominator = true_negative + false_positive
        specificity = true_negative / denominator if denominator else None
        class_binary = binary[:, offset]
        if len(np.unique(class_binary)) == 2:
            auroc = float(roc_auc_score(class_binary, probabilities[:, offset]))
            auprc = float(average_precision_score(class_binary, probabilities[:, offset]))
            aurocs.append(auroc)
            auprcs.append(auprc)
        else:
            auroc = auprc = None
        per_class.append(
            {
                "class_id": int(class_id),
                "Precision": float(precision[offset]),
                "Recall": float(recall[offset]),
                "Specificity": specificity,
                "F1": float(f1[offset]),
                "AUROC": auroc,
                "AUPRC": auprc,
                "Support": int(support[offset]),
                "metric_stability": (
                    "very_low_support" if int(support[offset]) < 5 else "standard"
                ),
            }
        )
    metrics = {
        "accuracy": float(accuracy_score(labels, predictions)),
        "balanced_accuracy": float(balanced_accuracy_score(labels, predictions)),
        "macro_f1": float(
            f1_score(labels, predictions, labels=class_ids, average="macro", zero_division=0)
        ),
        "weighted_f1": float(
            f1_score(
                labels,
                predictions,
                labels=class_ids,
                average="weighted",
                zero_division=0,
            )
        ),
        "top3_accuracy": _top_k_accuracy(labels, probabilities, 3),
        "top5_accuracy": _top_k_accuracy(labels, probabilities, 5),
        "macro_auroc": float(np.mean(aurocs)) if len(aurocs) == len(class_ids) else None,
        "macro_auprc": float(np.mean(auprcs)) if len(auprcs) == len(class_ids) else None,
    }
    return metrics, matrix, per_class


def _pipeline(c_value: float, class_weight: str | None, seed: int):
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    return Pipeline(
        [
            ("standard_scaler", StandardScaler()),
            (
                "classifier",
                LogisticRegression(
                    C=c_value,
                    class_weight=class_weight,
                    max_iter=4000,
                    random_state=seed,
                ),
            ),
        ]
    )


def _validate_and_select_rows(
    config: PrecomputedProbeConfig,
    features: np.ndarray,
) -> tuple[
    list[dict[str, str]],
    dict[int, tuple[int, str]],
    np.ndarray,
    np.ndarray,
    np.ndarray,
]:
    samples = _read_csv(config.samples)
    if len(samples) != len(features):
        raise ValueError("features rows must equal samples rows")
    sample_indices = [int(row["canonical_index"]) for row in samples]
    if sample_indices != list(range(len(samples))):
        raise ValueError("samples canonical_index must match feature row order")

    label_rows = _read_csv(config.labels)
    label_map: dict[int, tuple[int, str]] = {}
    for row in label_rows:
        canonical_index = int(row["canonical_index"])
        if canonical_index in label_map:
            raise ValueError(f"duplicate task label for canonical_index={canonical_index}")
        label_map[canonical_index] = (
            int(row["label"]),
            str(row.get("class_name") or row["label"]),
        )
    class_ids = np.array(sorted({label for label, _ in label_map.values()}), dtype=int)
    if class_ids.tolist() != list(range(len(class_ids))):
        raise ValueError("task labels must be contiguous integers starting at zero")

    split_rows = _read_csv(config.split_manifest)
    split_map = {int(row["canonical_index"]): row for row in split_rows}
    if len(split_map) != len(split_rows):
        raise ValueError("split manifest contains duplicate canonical_index values")
    missing = sorted(set(label_map) - set(split_map))
    if missing:
        raise ValueError(f"task labels are absent from split manifest: {missing[:5]}")
    development = np.array(
        sorted(index for index in label_map if split_map[index]["split"] == "development"),
        dtype=int,
    )
    test = np.array(
        sorted(index for index in label_map if split_map[index]["split"] == "test"),
        dtype=int,
    )
    if len(set(development) & set(test)) or len(development) + len(test) != len(label_map):
        raise ValueError("Development/Test must be disjoint and cover all task labels")
    folds = np.array([int(split_map[index]["cv_fold"]) for index in development], dtype=int)
    if sorted(set(folds)) != [0, 1, 2, 3, 4]:
        raise ValueError("Development split must contain exactly five CV folds")
    return samples, label_map, class_ids, development, test


def run_precomputed_probe(config: PrecomputedProbeConfig) -> Path:
    """Run a deterministic frozen-feature logistic-regression probe."""

    output = config.output_dir
    if output.exists() and any(output.iterdir()):
        raise ValueError(f"refusing to overwrite non-empty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)
    features = np.load(config.features, mmap_mode="r")
    if features.ndim != 2 or not np.isfinite(features).all():
        raise ValueError("features must be a finite two-dimensional array")
    samples, label_map, class_ids, development, test = _validate_and_select_rows(
        config,
        features,
    )
    split_rows = _read_csv(config.split_manifest)
    split_map = {int(row["canonical_index"]): row for row in split_rows}
    folds = np.array([int(split_map[index]["cv_fold"]) for index in development], dtype=int)
    development_labels = np.array([label_map[index][0] for index in development], dtype=int)
    test_labels = np.array([label_map[index][0] for index in test], dtype=int)
    development_features = np.asarray(features[development])
    test_features = np.asarray(features[test])

    cv_rows = []
    candidate_models = []
    for c_value in config.c_candidates:
        for class_weight in (None, "balanced"):
            fold_scores = []
            convergence_warnings = []
            for fold in range(5):
                train_mask = folds != fold
                validation_mask = folds == fold
                model = _pipeline(float(c_value), class_weight, config.seed)
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always")
                    model.fit(
                        development_features[train_mask],
                        development_labels[train_mask],
                    )
                convergence_warnings.extend(str(item.message) for item in caught)
                probabilities = model.predict_proba(development_features[validation_mask])
                fold_metrics, _, _ = _metrics(
                    development_labels[validation_mask],
                    probabilities,
                    class_ids,
                )
                fold_scores.append(fold_metrics)
            row = {
                "C": float(c_value),
                "class_weight": class_weight or "none",
                "mean_macro_f1": float(np.mean([item["macro_f1"] for item in fold_scores])),
                "std_macro_f1": float(np.std([item["macro_f1"] for item in fold_scores], ddof=1)),
                "mean_balanced_accuracy": float(
                    np.mean([item["balanced_accuracy"] for item in fold_scores])
                ),
                "mean_accuracy": float(np.mean([item["accuracy"] for item in fold_scores])),
                "convergence_warning_count": len(convergence_warnings),
            }
            cv_rows.append(row)
            candidate_models.append((row, float(c_value), class_weight))
    selected, selected_c, selected_weight = min(
        candidate_models,
        key=lambda item: (
            -item[0]["mean_macro_f1"],
            -item[0]["mean_balanced_accuracy"],
            0 if item[2] == "balanced" else 1,
            item[1],
        ),
    )
    final_model = _pipeline(selected_c, selected_weight, config.seed)
    final_model.fit(development_features, development_labels)
    probabilities = final_model.predict_proba(test_features)
    metrics, matrix, per_class = _metrics(test_labels, probabilities, class_ids)
    class_names = {
        class_id: next(name for label, name in label_map.values() if label == class_id)
        for class_id in class_ids
    }
    for row in per_class:
        row["class_name"] = class_names[row["class_id"]]

    _write_json(output / "metrics.json", metrics)
    _write_csv(
        output / "per_class.csv",
        per_class,
        [
            "class_id",
            "class_name",
            "Precision",
            "Recall",
            "Specificity",
            "F1",
            "AUROC",
            "AUPRC",
            "Support",
            "metric_stability",
        ],
    )
    _write_csv(output / "cv_results.csv", cv_rows, list(cv_rows[0]))
    _write_json(
        output / "selected_probe.json",
        {
            "type": "multinomial_logistic_regression",
            "selected_C": selected_c,
            "class_weight": selected_weight,
            "selection_metric": "Development five-fold mean Macro-F1",
            "test_used_for_selection": False,
            "standard_scaler_fit_scope": "each training fold",
            "cv_result": selected,
        },
    )
    _write_json(output / "confusion_matrix.json", matrix.tolist())
    task_metadata = {
        "display_name": config.task_display_name or config.task_id,
        "task_type": "single_label_multiclass_classification",
        "class_count": len(class_ids),
        "sample_count": len(label_map),
        "label_space": config.label_space or config.task_id,
        "label_semantics": "observed_directory_labels",
    }
    run_manifest = {
        "release_id": config.release_id,
        "model_id": config.model_id,
        "checkpoint_id": config.checkpoint_id,
        "adapter_version": config.adapter_version,
        "protocol_id": "precomputed-frozen-feature-logreg-v1",
        "task_id": config.task_id,
        "task_metadata": task_metadata,
        "qualification_status": "exploratory",
        "seed": config.seed,
        "development_size": len(development),
        "test_size": len(test),
        "feature_dim": int(features.shape[1]),
        "test_used_for_selection": False,
        "patient_id_available": False,
        "patient_level_generalization_not_established": True,
        "limitations": list(config.limitations),
        "confusion_matrix": matrix.tolist(),
    }
    _write_json(output / "run_manifest.json", run_manifest)
    _write_json(
        output / "summary.json",
        {
            "task": task_metadata,
            "metrics": metrics,
            "selected_probe": selected,
            "development_size": len(development),
            "test_size": len(test),
            "feature_alignment_verified": len(samples) == len(features),
            "development_test_disjoint": not bool(set(development) & set(test)),
            "test_used_for_selection": False,
        },
    )
    artifacts = sorted(
        path
        for path in output.iterdir()
        if path.is_file() and path.name != "artifact_manifest.json"
    )
    _write_json(
        output / "artifact_manifest.json",
        {path.name: _sha256(path) for path in artifacts},
    )
    return output
