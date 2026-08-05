from __future__ import annotations

from typing import Any

METRIC_ALIASES = {
    "macro_f1": "Macro-F1",
    "Macro F1": "Macro-F1",
    "balanced_accuracy": "Balanced Accuracy",
    "accuracy": "Accuracy",
    "top3_accuracy": "Top-3 Accuracy",
    "top_3_accuracy": "Top-3 Accuracy",
    "top5_accuracy": "Top-5 Accuracy",
    "top_5_accuracy": "Top-5 Accuracy",
    "macro_auroc": "Macro-AUROC",
    "macro_auc": "Macro-AUROC",
    "macro_auprc": "Macro-AUPRC",
    "macro_ap": "Macro-AUPRC",
    "weighted_f1": "Weighted-F1",
    "quadratic_weighted_kappa": "Quadratic Weighted Kappa",
    "quadratic_kappa": "Quadratic Weighted Kappa",
    "qwk": "Quadratic Weighted Kappa",
    "AP": "AUPRC",
    "ap": "AUPRC",
    "auprc": "AUPRC",
    "average_precision": "AUPRC",
    "auc": "AUROC",
    "recall": "Recall",
    "sensitivity": "Recall",
    "specificity": "Specificity",
    "f1": "F1",
    "support": "Support",
    "precision": "Precision",
}

SINGLE_LABEL_HOME_METRICS = (
    "Macro-F1",
    "Balanced Accuracy",
    "Accuracy",
    "Top-3 Accuracy",
    "Macro-AUROC",
)
SINGLE_LABEL_SECONDARY_METRICS = ("Top-5 Accuracy", "Weighted-F1")


def normalize_metrics(values: dict[str, Any]) -> dict[str, Any]:
    normalized = {}
    for key, value in values.items():
        name = METRIC_ALIASES.get(key, key)
        if value in ("", "NA", "N/A", None):
            normalized[name] = None
            continue
        try:
            normalized[name] = float(value)
        except (TypeError, ValueError):
            normalized[name] = value
    return normalized
