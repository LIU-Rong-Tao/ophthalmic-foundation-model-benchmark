#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageOps

CLASS_NAMES = {
    0: "No DR",
    1: "Mild",
    2: "Moderate",
    3: "Severe",
    4: "Proliferative DR",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _phash(image: Image.Image) -> int:
    from scipy.fft import dctn

    grayscale = (
        ImageOps.exif_transpose(image)
        .convert("L")
        .resize((32, 32), Image.Resampling.LANCZOS)
    )
    coefficients = dctn(np.asarray(grayscale, dtype=np.float32), type=2, norm="ortho")[:8, :8]
    flattened = coefficients.reshape(-1)
    median = float(np.median(flattened[1:]))
    bits = flattened > median
    value = 0
    for bit in bits:
        value = (value << 1) | int(bit)
    return value


def _read_labels(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for split, filename in (("development", "training_labels.txt"), ("test", "test_labels.txt")):
        path = root / filename
        with path.open(encoding="utf-8-sig") as handle:
            for line_number, line in enumerate(handle, start=1):
                relative_path, raw_values = line.strip().split(";", maxsplit=1)
                values = [int(item.strip()) for item in raw_values.split(",")]
                if len(values) != 13:
                    raise ValueError(f"{path}:{line_number}: expected 13 label values")
                active_grades = [index for index, value in enumerate(values[:5]) if value == 1]
                if len(active_grades) != 1:
                    raise ValueError(f"{path}:{line_number}: expected one active DR grade")
                label = active_grades[0]
                expected_aggregate = int(label > 0)
                if values[5] != expected_aggregate or any(values[6:]):
                    raise ValueError(f"{path}:{line_number}: inconsistent auxiliary labels")
                image_path = root / relative_path.strip()
                rows.append(
                    {
                        "relative_path": image_path.relative_to(root).as_posix(),
                        "sample_id": image_path.stem,
                        "label": label,
                        "class_name": CLASS_NAMES[label],
                        "split": split,
                        "source_label_file": filename,
                        "source_line": line_number,
                    }
                )
    return rows


def _components(edges: list[tuple[int, int]], size: int) -> list[list[int]]:
    parent = list(range(size))

    def find(item: int) -> int:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(left: int, right: int) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for left, right in edges:
        union(left, right)
    groups: dict[int, list[int]] = defaultdict(list)
    for index in range(size):
        groups[find(index)].append(index)
    return [indices for indices in groups.values() if len(indices) > 1]


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    temporary = path.with_suffix(".tmp.csv")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def _write_json(path: Path, payload: Any) -> None:
    temporary = path.with_suffix(".tmp.json")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _metadata_baseline(rows: list[dict[str, Any]]) -> dict[str, Any]:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
    from sklearn.model_selection import GridSearchCV, StratifiedKFold
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    features = np.asarray(
        [
            [
                row["width"],
                row["height"],
                row["width"] / row["height"],
                math.log1p(row["file_size"]),
            ]
            for row in rows
        ],
        dtype=np.float64,
    )
    labels = np.asarray([row["label"] for row in rows], dtype=np.int64)
    development = np.asarray([row["split"] == "development" for row in rows])
    pipeline = Pipeline(
        [
            ("scale", StandardScaler()),
            (
                "classifier",
                LogisticRegression(max_iter=4000, random_state=2026),
            ),
        ]
    )
    search = GridSearchCV(
        pipeline,
        {
            "classifier__C": [0.01, 0.1, 1.0, 10.0],
            "classifier__class_weight": [None, "balanced"],
        },
        scoring="f1_macro",
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=2026),
        n_jobs=1,
        refit=True,
    )
    search.fit(features[development], labels[development])
    predictions = search.predict(features[~development])
    return {
        "feature_names": ["width", "height", "aspect_ratio", "log_file_size"],
        "selection_scope": "development_five_fold_cv_only",
        "test_used_for_selection": False,
        "selected_parameters": search.best_params_,
        "test_accuracy": float(accuracy_score(labels[~development], predictions)),
        "test_balanced_accuracy": float(
            balanced_accuracy_score(labels[~development], predictions)
        ),
        "test_macro_f1": float(f1_score(labels[~development], predictions, average="macro")),
    }


def prepare(root: Path, output: Path, near_duplicate_distance: int = 4) -> None:
    rows = _read_labels(root)
    if len({row["sample_id"] for row in rows}) != len(rows):
        raise ValueError("APTOS sample_id values are not unique")
    output.mkdir(parents=True, exist_ok=False)

    failures: list[dict[str, Any]] = []
    readable_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        image_path = root / row["relative_path"]
        try:
            with Image.open(image_path) as image:
                image.load()
                width, height = image.size
                perceptual_hash = _phash(image)
            enriched = {
                **row,
                "canonical_index": index,
                "file_size": image_path.stat().st_size,
                "width": width,
                "height": height,
                "sha256": _sha256(image_path),
                "phash": f"{perceptual_hash:016x}",
                "_phash_int": perceptual_hash,
            }
            readable_rows.append(enriched)
        except Exception as exc:
            failures.append(
                {
                    "sample_id": row["sample_id"],
                    "relative_path": row["relative_path"],
                    "exception_type": type(exc).__name__,
                    "sanitized_error": str(exc)[:300],
                }
            )
    if failures:
        _write_csv(
            output / "failures.csv",
            failures,
            ["sample_id", "relative_path", "exception_type", "sanitized_error"],
        )
        raise RuntimeError(f"{len(failures)} images failed decoding; benchmark preparation stopped")

    exact_edges: list[tuple[int, int]] = []
    by_sha: dict[str, list[int]] = defaultdict(list)
    for offset, row in enumerate(readable_rows):
        by_sha[row["sha256"]].append(offset)
    for indices in by_sha.values():
        exact_edges.extend((indices[0], index) for index in indices[1:])
    exact_groups = _components(exact_edges, len(readable_rows))

    near_edges: list[tuple[int, int]] = []
    for left in range(len(readable_rows)):
        left_hash = readable_rows[left]["_phash_int"]
        for right in range(left + 1, len(readable_rows)):
            distance = (left_hash ^ readable_rows[right]["_phash_int"]).bit_count()
            if distance <= near_duplicate_distance:
                near_edges.append((left, right))
    near_groups = _components(near_edges, len(readable_rows))

    exact_rows: list[dict[str, Any]] = []
    for group_id, indices in enumerate(exact_groups):
        for offset in indices:
            row = readable_rows[offset]
            exact_rows.append(
                {
                    "duplicate_group": f"exact-{group_id:04d}",
                    "sample_id": row["sample_id"],
                    "relative_path": row["relative_path"],
                    "label": row["label"],
                    "split": row["split"],
                    "sha256": row["sha256"],
                }
            )
    near_rows: list[dict[str, Any]] = []
    for group_id, indices in enumerate(near_groups):
        for offset in indices:
            row = readable_rows[offset]
            near_rows.append(
                {
                    "duplicate_group": f"phash-{group_id:04d}",
                    "sample_id": row["sample_id"],
                    "relative_path": row["relative_path"],
                    "label": row["label"],
                    "split": row["split"],
                    "phash": row["phash"],
                }
            )

    development_indices = [
        row["canonical_index"] for row in readable_rows if row["split"] == "development"
    ]
    development_labels = np.asarray(
        [row["label"] for row in readable_rows if row["split"] == "development"]
    )
    from sklearn.model_selection import StratifiedKFold

    folds: dict[int, int] = {}
    splitter = StratifiedKFold(n_splits=5, shuffle=True, random_state=2026)
    dummy = np.zeros(len(development_indices))
    for fold, (_, validation_offsets) in enumerate(splitter.split(dummy, development_labels)):
        for offset in validation_offsets:
            folds[development_indices[offset]] = fold

    manifest_rows: list[dict[str, Any]] = []
    label_rows: list[dict[str, Any]] = []
    sample_rows: list[dict[str, Any]] = []
    split_rows: list[dict[str, Any]] = []
    for row in readable_rows:
        manifest_rows.append(
            {
                "row_index": row["canonical_index"],
                "sample_id": row["sample_id"],
                "image_path": str((root / row["relative_path"]).resolve()),
                "relative_path": row["relative_path"],
                "label": row["label"],
                "class_name": row["class_name"],
                "split": row["split"],
            }
        )
        label_rows.append(
            {
                "canonical_index": row["canonical_index"],
                "label": row["label"],
                "class_name": row["class_name"],
            }
        )
        sample_rows.append(
            {
                "canonical_index": row["canonical_index"],
                "sample_id": row["sample_id"],
                "relative_path": row["relative_path"],
            }
        )
        split_rows.append(
            {
                "canonical_index": row["canonical_index"],
                "sample_id": row["sample_id"],
                "split": row["split"],
                "cv_fold": folds.get(row["canonical_index"], ""),
            }
        )

    exact_cross_split = sum(
        len({readable_rows[index]["split"] for index in group}) > 1 for group in exact_groups
    )
    near_cross_split = sum(
        len({readable_rows[index]["split"] for index in group}) > 1 for group in near_groups
    )
    audit = {
        "dataset_id": "aptos2019",
        "task": "ICDR diabetic retinopathy grade 0-4",
        "source_semantics": "processed copy of the public APTOS 2019 training set",
        "split_provenance": "pre-existing 80/20 split documented by the local dataset Readme",
        "split_seed_provenance": "not_documented",
        "patient_id_available": False,
        "patient_level_leakage_status": "cannot_be_fully_assessed",
        "patient_level_generalization_not_established": True,
        "sample_count": len(readable_rows),
        "development_count": len(development_indices),
        "test_count": len(readable_rows) - len(development_indices),
        "class_distribution_all": dict(
            sorted(Counter(str(row["label"]) for row in readable_rows).items())
        ),
        "class_distribution_development": dict(
            sorted(
                Counter(
                    str(row["label"])
                    for row in readable_rows
                    if row["split"] == "development"
                ).items()
            )
        ),
        "class_distribution_test": dict(
            sorted(
                Counter(
                    str(row["label"]) for row in readable_rows if row["split"] == "test"
                ).items()
            )
        ),
        "readable_count": len(readable_rows),
        "failure_count": len(failures),
        "exact_duplicate_group_count": len(exact_groups),
        "exact_duplicate_cross_split_group_count": exact_cross_split,
        "phash_distance_threshold": near_duplicate_distance,
        "near_duplicate_group_count": len(near_groups),
        "near_duplicate_cross_split_group_count": near_cross_split,
        "metadata_only_baseline": _metadata_baseline(readable_rows),
        "network_access_used": False,
        "external_upload_used": False,
    }
    _write_csv(
        output / "manifest.csv",
        manifest_rows,
        [
            "row_index",
            "sample_id",
            "image_path",
            "relative_path",
            "label",
            "class_name",
            "split",
        ],
    )
    _write_csv(
        output / "labels.csv",
        label_rows,
        ["canonical_index", "label", "class_name"],
    )
    _write_csv(
        output / "samples.csv",
        sample_rows,
        ["canonical_index", "sample_id", "relative_path"],
    )
    _write_csv(
        output / "split_manifest_seed2026.csv",
        split_rows,
        ["canonical_index", "sample_id", "split", "cv_fold"],
    )
    _write_csv(
        output / "exact_duplicate_groups.csv",
        exact_rows,
        ["duplicate_group", "sample_id", "relative_path", "label", "split", "sha256"],
    )
    _write_csv(
        output / "near_duplicate_groups.csv",
        near_rows,
        ["duplicate_group", "sample_id", "relative_path", "label", "split", "phash"],
    )
    _write_json(output / "dataset_audit.json", audit)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--near-duplicate-distance", type=int, default=4)
    args = parser.parse_args()
    prepare(args.data_root.resolve(), args.output.resolve(), args.near_duplicate_distance)


if __name__ == "__main__":
    main()
