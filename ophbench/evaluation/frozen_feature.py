from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from ophbench import __version__, load_adapter

EXPECTED_CLASSES = (
    "anodr",
    "bmilddr",
    "cmoderatedr",
    "dseveredr",
    "eproliferativedr",
)
FORBIDDEN_PROTOCOL_FIELDS = {
    "optimizer",
    "scheduler",
    "loss",
    "epoch",
    "epochs",
    "augmentation",
    "learning_rate",
}
OUTPUT_FILES = {
    "protocol.yaml",
    "effective_config.yaml",
    "split_manifest.csv",
    "split_manifest.json",
    "run_manifest.json",
    "validation_results.csv",
    "selected_probe.json",
    "test_predictions.csv",
    "metrics.json",
    "bootstrap_summary.csv",
    "confusion_matrix.csv",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_state(root: Path) -> tuple[str, bool]:
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip()
    dirty = bool(
        subprocess.check_output(
            ["git", "status", "--porcelain", "--untracked-files=no"], cwd=root, text=True
        ).strip()
    )
    return commit, dirty


def load_protocol(path: Path | str) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("protocol root must be a mapping")
    forbidden = FORBIDDEN_PROTOCOL_FIELDS & set(payload)
    if forbidden:
        raise ValueError(f"Frozen feature protocol contains irrelevant fields: {sorted(forbidden)}")
    if payload.get("track") != "frozen_feature_transfer":
        raise ValueError("track must be frozen_feature_transfer")
    if str(payload.get("protocol_version")) != "0.1":
        raise ValueError("only protocol_version=0.1 is supported")
    model, task, probe, evaluation = (
        payload.get("model", {}),
        payload.get("task", {}),
        payload.get("probe", {}),
        payload.get("evaluation", {}),
    )
    if model.get("encoder_frozen") is not True or model.get("preprocessing") != "model_native":
        raise ValueError("v0.1 requires a frozen encoder and model_native preprocessing")
    if probe.get("type") != "logistic_regression":
        raise ValueError("v0.1 only supports logistic_regression")
    if probe.get("selection_split") != "val" or probe.get("selection_metric") != "macro_f1":
        raise ValueError("probe selection must use val macro_f1")
    if evaluation.get("test_not_used_for_selection") is not True:
        raise ValueError("test_not_used_for_selection must be true")
    if int(task.get("num_classes", 0)) != 5:
        raise ValueError("APTOS pilot requires five classes")
    return payload


def build_split_manifest(data_root: Path | str) -> tuple[pd.DataFrame, dict[str, Any]]:
    from torchvision.datasets import ImageFolder

    root = Path(data_root)
    rows = []
    split_keys: dict[str, set[str]] = {}
    distributions = {}
    for split in ("train", "val", "test"):
        dataset = ImageFolder(root / split)
        if tuple(dataset.classes) != EXPECTED_CLASSES:
            raise ValueError(f"{split} class order mismatch: {dataset.classes}")
        keys = set()
        counts = {str(index): 0 for index in range(5)}
        for path, label in dataset.samples:
            relative_path = Path(path).relative_to(root).as_posix()
            key = Path(path).stem
            if key in keys:
                raise ValueError(f"duplicate image key within {split}: {key}")
            keys.add(key)
            counts[str(label)] += 1
            rows.append(
                {
                    "split": split,
                    "relative_path": relative_path,
                    "image_key": key,
                    "label": int(label),
                }
            )
        split_keys[split] = keys
        distributions[split] = {"samples": len(dataset), "class_distribution": counts}
    overlaps = {}
    for left, right in (("train", "val"), ("train", "test"), ("val", "test")):
        overlap = sorted(split_keys[left] & split_keys[right])
        overlaps[f"{left}_{right}"] = len(overlap)
        if overlap:
            raise ValueError(f"split image key overlap: {left}/{right}: {overlap[:5]}")
    frame = pd.DataFrame(rows).sort_values(["split", "relative_path"]).reset_index(drop=True)
    stable_csv = frame.to_csv(index=False, lineterminator="\n")
    fingerprint = hashlib.sha256(stable_csv.encode("utf-8")).hexdigest()
    metadata = {
        "split_level": "image",
        "patient_id_available": False,
        "patient_level_claim_allowed": False,
        "splits": distributions,
        "duplicate_image_key_counts": overlaps,
        "split_manifest_sha256": fingerprint,
    }
    return frame, metadata


def _extract_embeddings(adapter, data_root: Path, manifest: pd.DataFrame, batch_size: int):
    import torch
    from PIL import Image

    features = []
    for start in range(0, len(manifest), batch_size):
        batch = manifest.iloc[start : start + batch_size]
        tensors = []
        for relative_path in batch["relative_path"]:
            with Image.open(data_root / relative_path) as image:
                tensors.append(adapter.preprocess(image))
        encoded = adapter.encode_image(torch.stack(tensors)).detach().cpu().numpy()
        features.append(encoded)
    return np.concatenate(features)


def _classification_metrics(labels, probabilities) -> tuple[dict[str, Any], np.ndarray]:
    from sklearn.metrics import accuracy_score, cohen_kappa_score, confusion_matrix, f1_score

    predictions = probabilities.argmax(axis=1)
    matrix = confusion_matrix(labels, predictions, labels=list(range(5)))
    recalls = np.divide(
        np.diag(matrix),
        matrix.sum(axis=1),
        out=np.zeros(5, dtype=float),
        where=matrix.sum(axis=1) > 0,
    )
    return (
        {
            "quadratic_kappa": float(cohen_kappa_score(labels, predictions, weights="quadratic")),
            "macro_f1": float(f1_score(labels, predictions, average="macro")),
            "accuracy": float(accuracy_score(labels, predictions)),
            "per_class_recall": {str(index): float(value) for index, value in enumerate(recalls)},
        },
        matrix,
    )


def _bootstrap(labels, probabilities, *, resamples: int, confidence_level: float, seed: int):
    rng = np.random.default_rng(seed)
    metric_names = ("quadratic_kappa", "macro_f1", "accuracy")
    values = {name: [] for name in metric_names}
    for _ in range(resamples):
        indices = rng.integers(0, len(labels), size=len(labels))
        metrics, _ = _classification_metrics(labels[indices], probabilities[indices])
        for name in metric_names:
            values[name].append(metrics[name])
    alpha = (1.0 - confidence_level) / 2.0
    return pd.DataFrame(
        [
            {
                "metric": name,
                "estimate": float(np.mean(samples)),
                "ci_lower": float(np.quantile(samples, alpha)),
                "ci_upper": float(np.quantile(samples, 1.0 - alpha)),
                "confidence_level": confidence_level,
                "bootstrap_unit": "image",
                "resamples": resamples,
                "seed": seed,
            }
            for name, samples in values.items()
        ]
    )


def run_frozen_feature_transfer(
    protocol_path: Path | str,
    *,
    data_root: Path | str,
    checkpoint_path: Path | str,
    output_dir: Path | str,
    device: str = "cuda:0",
    batch_size: int = 32,
    adapter_factory: Callable[..., Any] = load_adapter,
) -> Path:
    import torch
    from sklearn.linear_model import LogisticRegression

    protocol_path, data_root, checkpoint_path, output_dir = map(
        Path, (protocol_path, data_root, checkpoint_path, output_dir)
    )
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError(f"refusing to overwrite non-empty output directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    protocol = load_protocol(protocol_path)
    checkpoint_sha256 = _sha256(checkpoint_path)
    manifest, split_metadata = build_split_manifest(data_root)
    effective = {
        **protocol,
        "runtime": {
            "data_root": str(data_root.resolve()),
            "checkpoint_path": str(checkpoint_path.resolve()),
            "output_dir": str(output_dir.resolve()),
            "device": device,
            "batch_size": batch_size,
        },
    }
    (output_dir / "protocol.yaml").write_text(
        protocol_path.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (output_dir / "effective_config.yaml").write_text(
        yaml.safe_dump(effective, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    manifest.to_csv(output_dir / "split_manifest.csv", index=False, lineterminator="\n")
    (output_dir / "split_manifest.json").write_text(
        json.dumps({**split_metadata, "entries": manifest.to_dict("records")}, indent=2),
        encoding="utf-8",
    )
    adapter = adapter_factory(
        model_id=protocol["model"]["model_id"],
        checkpoint_id=protocol["model"]["checkpoint_id"],
        checkpoint_path=checkpoint_path,
        device=device,
    ).load()
    features = {}
    labels = {}
    split_frames = {}
    for split in ("train", "val", "test"):
        split_frame = manifest.loc[manifest["split"].eq(split)].reset_index(drop=True)
        split_frames[split] = split_frame
        labels[split] = split_frame["label"].to_numpy(int)
        features[split] = _extract_embeddings(adapter, data_root, split_frame, batch_size)
    validation_rows = []
    classifiers = []
    probe = protocol["probe"]
    for c_value in probe["c_candidates"]:
        classifier = LogisticRegression(
            C=float(c_value), max_iter=int(probe["max_iter"]), random_state=int(probe["seed"])
        )
        classifier.fit(features["train"], labels["train"])
        probability = classifier.predict_proba(features["val"])
        metrics, _ = _classification_metrics(labels["val"], probability)
        validation_rows.append({"C": float(c_value), **metrics})
        classifiers.append(classifier)
    validation = pd.DataFrame(validation_rows)
    selected_index = int(validation["macro_f1"].to_numpy().argmax())
    selected_c = float(validation.iloc[selected_index]["C"])
    classifier = classifiers[selected_index]
    if classifier.classes_.tolist() != [0, 1, 2, 3, 4]:
        raise ValueError(f"probe classes mismatch: {classifier.classes_.tolist()}")
    validation.to_csv(output_dir / "validation_results.csv", index=False)
    (output_dir / "selected_probe.json").write_text(
        json.dumps(
            {
                "type": "logistic_regression",
                "selected_C": selected_c,
                "selection_split": "val",
                "selection_metric": "macro_f1",
                "test_used_for_selection": False,
                "classes": classifier.classes_.tolist(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    test_probabilities = classifier.predict_proba(features["test"])
    test_metrics, matrix = _classification_metrics(labels["test"], test_probabilities)
    predictions = split_frames["test"][["image_key", "relative_path", "label"]].rename(
        columns={"label": "true_label"}
    )
    predictions["pred_label"] = test_probabilities.argmax(axis=1)
    for index in range(5):
        predictions[f"prob_{index}"] = test_probabilities[:, index]
    predictions.to_csv(output_dir / "test_predictions.csv", index=False)
    pd.DataFrame(matrix, index=range(5), columns=range(5)).to_csv(
        output_dir / "confusion_matrix.csv", index_label="true_label"
    )
    bootstrap_config = protocol["evaluation"]["bootstrap"]
    bootstrap = _bootstrap(
        labels["test"],
        test_probabilities,
        resamples=int(bootstrap_config["resamples"]),
        confidence_level=float(bootstrap_config["confidence_level"]),
        seed=int(bootstrap_config["seed"]),
    )
    bootstrap.to_csv(output_dir / "bootstrap_summary.csv", index=False)
    (output_dir / "metrics.json").write_text(
        json.dumps(
            {
                "primary_metric": "quadratic_kappa",
                "test_metrics": test_metrics,
                "confusion_matrix": matrix.tolist(),
                "bootstrap_unit": "image",
                "patient_level_claim_allowed": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    repo_root = Path(__file__).resolve().parents[2]
    git_commit, git_dirty = _git_state(repo_root)
    run_manifest = {
        "track": "frozen_feature_transfer",
        "protocol_version": "0.1",
        "evaluation_role": "pilot_protocol_validation",
        "research_claim_status": "not_for_scientific_comparison",
        "model_id": protocol["model"]["model_id"],
        "checkpoint_id": protocol["model"]["checkpoint_id"],
        "task_id": protocol["task"]["task_id"],
        "dataset_id": protocol["task"]["dataset_id"],
        "source_git_commit": git_commit,
        "source_git_dirty": git_dirty,
        "ophbench_version": __version__,
        "adapter_version": str(getattr(adapter, "adapter_version", "unknown")),
        "checkpoint_sha256": checkpoint_sha256,
        "split_manifest_sha256": split_metadata["split_manifest_sha256"],
        "split_level": "image",
        "patient_id_available": False,
        "patient_level_claim_allowed": False,
        "seed": int(probe["seed"]),
        "selected_C": selected_c,
        "python": platform.python_version(),
        "pytorch": torch.__version__,
        "cuda": torch.version.cuda,
        "device": device,
        "test_used_for_selection": False,
    }
    (output_dir / "run_manifest.json").write_text(
        json.dumps(run_manifest, indent=2), encoding="utf-8"
    )
    artifact_files = sorted(OUTPUT_FILES)
    artifact_manifest = {
        "schema_version": 1,
        "self_included": False,
        "artifacts": [
            {
                "name": name,
                "size_bytes": (output_dir / name).stat().st_size,
                "sha256": _sha256(output_dir / name),
            }
            for name in artifact_files
        ],
    }
    (output_dir / "artifact_manifest.json").write_text(
        json.dumps(artifact_manifest, indent=2), encoding="utf-8"
    )
    return output_dir


def compare_reproduction_runs(first: Path | str, second: Path | str) -> dict[str, Any]:
    first, second = Path(first), Path(second)
    selected_first = json.loads((first / "selected_probe.json").read_text())["selected_C"]
    selected_second = json.loads((second / "selected_probe.json").read_text())["selected_C"]
    predictions_equal = (first / "test_predictions.csv").read_bytes() == (
        second / "test_predictions.csv"
    ).read_bytes()
    metrics_equal = (first / "metrics.json").read_bytes() == (second / "metrics.json").read_bytes()
    manifest_first = json.loads((first / "run_manifest.json").read_text())
    manifest_second = json.loads((second / "run_manifest.json").read_text())
    result = {
        "selected_C_equal": selected_first == selected_second,
        "predictions_equal": predictions_equal,
        "metrics_equal": metrics_equal,
        "split_fingerprint_equal": (
            manifest_first["split_manifest_sha256"] == manifest_second["split_manifest_sha256"]
        ),
    }
    result["reproducible"] = all(result.values())
    return result
