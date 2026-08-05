#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageOps
from prepare_aptos2019_benchmark import _metadata_baseline, _write_csv, _write_json

SEEDS = (2026, 2027, 2028, 2029, 2030)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _components(edges: list[tuple[str, str]]) -> list[list[str]]:
    members = sorted({item for edge in edges for item in edge})
    parent = {item: item for item in members}

    def find(item: str) -> str:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    for left, right in edges:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root
    groups: dict[str, list[str]] = defaultdict(list)
    for item in members:
        groups[find(item)].append(item)
    return [values for values in groups.values() if len(values) > 1]


def _fundus_signature(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        rgb = np.asarray(ImageOps.exif_transpose(image).convert("RGB"))
    grayscale = rgb.mean(axis=2)
    mask = grayscale > 12
    coordinates = np.argwhere(mask)
    if len(coordinates):
        top, left = coordinates.min(axis=0)
        bottom, right = coordinates.max(axis=0) + 1
        rgb = rgb[top:bottom, left:right]
    resized = Image.fromarray(rgb).resize((128, 128), Image.Resampling.LANCZOS)
    values = np.asarray(resized.convert("L"), dtype=np.float32) / 255.0
    return (values - values.mean()) / (values.std() + 1e-6)


def _decontaminate(
    source_rows: list[dict[str, str]],
    exact_rows: list[dict[str, str]],
    near_rows: list[dict[str, str]],
    data_root: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    by_sample = {row["sample_id"]: dict(row) for row in source_rows}
    dispositions = {
        sample_id: {
            "sample_id": sample_id,
            "relative_path": row["relative_path"],
            "label": row["label"],
            "status": "retained",
            "duplicate_group": "",
            "representative_sample_id": sample_id,
        }
        for sample_id, row in by_sample.items()
    }
    exact_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in exact_rows:
        exact_groups[row["duplicate_group"]].append(row)
    for group_id, rows in exact_groups.items():
        sample_ids = sorted(row["sample_id"] for row in rows)
        labels = {row["label"] for row in rows}
        if len(labels) > 1:
            for sample_id in sample_ids:
                dispositions[sample_id].update(
                    {
                        "status": "excluded_exact_label_conflict",
                        "duplicate_group": group_id,
                        "representative_sample_id": "",
                    }
                )
            continue
        representative = sample_ids[0]
        for sample_id in sample_ids:
            dispositions[sample_id].update(
                {
                    "status": (
                        "retained" if sample_id == representative else "collapsed_exact_duplicate"
                    ),
                    "duplicate_group": group_id,
                    "representative_sample_id": representative,
                }
            )

    retained = {
        sample_id
        for sample_id, disposition in dispositions.items()
        if disposition["status"] == "retained"
    }
    candidate_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in near_rows:
        if row["sample_id"] in retained:
            candidate_groups[row["duplicate_group"]].append(row)
    candidate_ids = sorted(
        {
            row["sample_id"]
            for rows in candidate_groups.values()
            for row in rows
        }
    )
    signatures = {
        sample_id: _fundus_signature(data_root / by_sample[sample_id]["relative_path"])
        for sample_id in candidate_ids
    }
    verified_edges: list[tuple[str, str]] = []
    comparison_rows: list[dict[str, Any]] = []
    for candidate_group, rows in candidate_groups.items():
        ordered = sorted(rows, key=lambda row: row["sample_id"])
        signature_matrix = np.stack(
            [signatures[row["sample_id"]].reshape(-1) for row in ordered]
        )
        flipped_matrix = np.stack(
            [np.fliplr(signatures[row["sample_id"]]).reshape(-1) for row in ordered]
        )
        normalization = signature_matrix.shape[1]
        direct_correlations = signature_matrix @ signature_matrix.T / normalization
        flipped_correlations = signature_matrix @ flipped_matrix.T / normalization
        for left_offset, left_row in enumerate(ordered):
            for right_offset in range(left_offset + 1, len(ordered)):
                right_row = ordered[right_offset]
                distance = (
                    int(left_row["phash"], 16) ^ int(right_row["phash"], 16)
                ).bit_count()
                if distance > 4:
                    continue
                direct_correlation = float(direct_correlations[left_offset, right_offset])
                flipped_correlation = float(flipped_correlations[left_offset, right_offset])
                if flipped_correlation > direct_correlation:
                    correlation = flipped_correlation
                    right_signature = np.fliplr(signatures[right_row["sample_id"]])
                else:
                    correlation = direct_correlation
                    right_signature = signatures[right_row["sample_id"]]
                normalized_mae = (
                    float(
                        np.mean(
                            np.abs(
                                signatures[left_row["sample_id"]]
                                - right_signature
                            )
                        )
                    )
                    if correlation >= 0.995
                    else float("nan")
                )
                verified = correlation >= 0.995 and normalized_mae <= 0.08
                comparison_rows.append(
                    {
                        "candidate_group": candidate_group,
                        "left_sample_id": left_row["sample_id"],
                        "right_sample_id": right_row["sample_id"],
                        "phash_distance": distance,
                        "correlation": correlation,
                        "normalized_mae": normalized_mae,
                        "verified_high_confidence": verified,
                    }
                )
                if verified:
                    verified_edges.append((left_row["sample_id"], right_row["sample_id"]))

    near_groups = _components(verified_edges)
    near_group_rows: list[dict[str, Any]] = []
    for group_index, sample_ids in enumerate(near_groups):
        group_id = f"near-{group_index:04d}"
        labels = {by_sample[sample_id]["label"] for sample_id in sample_ids}
        representative = min(sample_ids)
        for sample_id in sample_ids:
            if len(labels) > 1:
                status = "excluded_near_label_conflict"
                selected_representative = ""
            else:
                status = "retained" if sample_id == representative else "collapsed_near_duplicate"
                selected_representative = representative
            dispositions[sample_id].update(
                {
                    "status": status,
                    "duplicate_group": group_id,
                    "representative_sample_id": selected_representative,
                }
            )
            near_group_rows.append(
                {
                    "duplicate_group": group_id,
                    "sample_id": sample_id,
                    "relative_path": by_sample[sample_id]["relative_path"],
                    "label": by_sample[sample_id]["label"],
                    "status": status,
                }
            )
    final_rows = [
        by_sample[sample_id]
        for sample_id, disposition in dispositions.items()
        if disposition["status"] == "retained"
    ]
    final_rows.sort(key=lambda row: row["sample_id"])
    return final_rows, list(dispositions.values()), comparison_rows + near_group_rows


def _split_rows(rows: list[dict[str, Any]], seed: int) -> list[dict[str, Any]]:
    from sklearn.model_selection import StratifiedKFold, train_test_split

    indices = np.arange(len(rows))
    labels = np.asarray([int(row["label"]) for row in rows])
    development, test = train_test_split(
        indices,
        test_size=0.15,
        random_state=seed,
        shuffle=True,
        stratify=labels,
    )
    development = np.sort(development)
    test_set = set(map(int, test))
    folds: dict[int, int] = {}
    splitter = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    for fold, (_, validation) in enumerate(
        splitter.split(np.zeros(len(development)), labels[development])
    ):
        for offset in validation:
            folds[int(development[offset])] = fold
    return [
        {
            "canonical_index": index,
            "sample_id": row["sample_id"],
            "split": "test" if index in test_set else "development",
            "cv_fold": "" if index in test_set else folds[index],
        }
        for index, row in enumerate(rows)
    ]


def prepare(source_audit: Path, data_root: Path, output: Path) -> None:
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {output}")
    source_rows = _read_csv(source_audit / "manifest.csv")
    exact_rows = _read_csv(source_audit / "exact_duplicate_groups.csv")
    near_rows = _read_csv(source_audit / "near_duplicate_groups.csv")
    final_rows, dispositions, near_details = _decontaminate(
        source_rows,
        exact_rows,
        near_rows,
        data_root,
    )
    output.mkdir(parents=True)
    main_split = _split_rows(final_rows, 2026)
    main_split_by_index = {int(row["canonical_index"]): row for row in main_split}
    benchmark_rows: list[dict[str, Any]] = []
    labels: list[dict[str, Any]] = []
    samples: list[dict[str, Any]] = []
    metadata_rows: list[dict[str, Any]] = []
    for index, row in enumerate(final_rows):
        split = main_split_by_index[index]["split"]
        benchmark_rows.append(
            {
                "row_index": index,
                "sample_id": row["sample_id"],
                "image_path": row["image_path"],
                "relative_path": row["relative_path"],
                "label": row["label"],
                "class_name": row["class_name"],
                "split": split,
            }
        )
        labels.append(
            {
                "canonical_index": index,
                "label": row["label"],
                "class_name": row["class_name"],
            }
        )
        samples.append(
            {
                "canonical_index": index,
                "sample_id": row["sample_id"],
                "relative_path": row["relative_path"],
            }
        )
        image_path = data_root / row["relative_path"]
        with Image.open(image_path) as image:
            width, height = image.size
        metadata_rows.append(
            {
                "width": width,
                "height": height,
                "file_size": image_path.stat().st_size,
                "label": int(row["label"]),
                "split": split,
            }
        )
    for seed in SEEDS:
        _write_csv(
            output / f"split_manifest_seed{seed}.csv",
            _split_rows(final_rows, seed),
            ["canonical_index", "sample_id", "split", "cv_fold"],
        )
    _write_csv(
        output / "manifest.csv",
        benchmark_rows,
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
        labels,
        ["canonical_index", "label", "class_name"],
    )
    _write_csv(
        output / "samples.csv",
        samples,
        ["canonical_index", "sample_id", "relative_path"],
    )
    _write_csv(
        output / "source_disposition.csv",
        dispositions,
        [
            "sample_id",
            "relative_path",
            "label",
            "status",
            "duplicate_group",
            "representative_sample_id",
        ],
    )
    near_fields = (
        list(near_details[0])
        if near_details
        else [
            "candidate_group",
            "left_sample_id",
            "right_sample_id",
            "phash_distance",
            "correlation",
            "normalized_mae",
            "verified_high_confidence",
        ]
    )
    comparison_rows = [
        row for row in near_details if "verified_high_confidence" in row
    ]
    _write_csv(output / "near_duplicate_comparisons.csv", comparison_rows, near_fields)
    statuses = Counter(row["status"] for row in dispositions)
    audit = {
        "dataset_id": "aptos2019-decontaminated",
        "task": "ICDR diabetic retinopathy grade 0-4",
        "duplicate_decontamination_applied": True,
        "failure_count": 0,
        "source_record_count": len(source_rows),
        "canonical_sample_count": len(final_rows),
        "class_distribution": dict(
            sorted(Counter(str(row["label"]) for row in final_rows).items())
        ),
        "source_disposition_counts": dict(sorted(statuses.items())),
        "exact_label_conflict_records_excluded": statuses[
            "excluded_exact_label_conflict"
        ],
        "exact_duplicate_records_collapsed": statuses["collapsed_exact_duplicate"],
        "near_label_conflict_records_excluded": statuses[
            "excluded_near_label_conflict"
        ],
        "near_duplicate_records_collapsed": statuses["collapsed_near_duplicate"],
        "exact_duplicate_groups_remaining": 0,
        "high_confidence_near_duplicate_groups_remaining": 0,
        "split_method": "stratified_random_after_duplicate_decontamination",
        "test_fraction": 0.15,
        "main_seed": 2026,
        "robustness_seeds": list(SEEDS),
        "patient_id_available": False,
        "patient_level_leakage_status": "cannot_be_fully_assessed",
        "patient_level_generalization_not_established": True,
        "metadata_only_baseline": _metadata_baseline(metadata_rows),
        "network_access_used": False,
        "external_upload_used": False,
    }
    _write_json(output / "dataset_audit.json", audit)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-audit", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.source_audit.resolve(), args.data_root.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
