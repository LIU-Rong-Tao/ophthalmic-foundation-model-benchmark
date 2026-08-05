#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

import numpy as np

SEEDS = (2026, 2027, 2028, 2029, 2030)
MODELS = (
    ("retfound", "retfound-cfp", 8),
    ("retfound-green", "retfound-green-v0.1", 8),
    ("eyeclip", "eyeclip-default", 8),
    ("flair", "flair-default", 8),
    ("keepfit", "keepfit-flair-mmretinal-cfp", 8),
    ("ret-clip", "ret-clip-default", 8),
    ("vilref", "vilref-default", 8),
    ("retizero", "retizero-default", 4),
    ("urfound", "urfound-default", 8),
)


def _environment() -> dict[str, str]:
    values = dict(os.environ)
    for key in (
        "http_proxy",
        "https_proxy",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "all_proxy",
    ):
        values.pop(key, None)
    values.update(
        {
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            "OMP_NUM_THREADS": "2",
            "MKL_NUM_THREADS": "2",
            "OPENBLAS_NUM_THREADS": "2",
        }
    )
    return values


def _run(command: list[str], *, cwd: Path, log: Path | None = None) -> None:
    if log is None:
        subprocess.run(command, cwd=cwd, env=_environment(), check=True)
        return
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("w", encoding="utf-8") as handle:
        subprocess.run(
            command,
            cwd=cwd,
            env=_environment(),
            stdout=handle,
            stderr=subprocess.STDOUT,
            check=True,
        )


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    temporary = path.with_suffix(".tmp.csv")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _validate_audit(audit_dir: Path) -> dict[str, Any]:
    audit = json.loads((audit_dir / "dataset_audit.json").read_text(encoding="utf-8"))
    required = {
        "dataset_id": "aptos2019-decontaminated",
        "network_access_used": False,
        "external_upload_used": False,
    }
    mismatches = {
        key: {"expected": expected, "actual": audit.get(key)}
        for key, expected in required.items()
        if audit.get(key) != expected
    }
    if mismatches:
        raise RuntimeError(f"APTOS audit gate failed: {mismatches}")
    if int(audit.get("canonical_sample_count") or 0) < 3000:
        raise RuntimeError("APTOS decontamination retained unexpectedly few samples")
    dispositions = audit.get("source_disposition_counts") or {}
    if dispositions.get("retained") != audit.get("canonical_sample_count"):
        raise RuntimeError("APTOS retained sample count does not match source dispositions")
    return audit


def _ensure_probe_inputs(audit_dir: Path, expected_count: int) -> None:
    manifest = _read_csv(audit_dir / "manifest.csv")
    labels = _read_csv(audit_dir / "labels.csv")
    if len(manifest) != expected_count or len(labels) != expected_count:
        raise RuntimeError("APTOS manifest and label row counts do not match the audit")
    samples_path = audit_dir / "samples.csv"
    if not samples_path.is_file():
        _write_csv(
            samples_path,
            [
                {
                    "canonical_index": row["row_index"],
                    "sample_id": row["sample_id"],
                    "relative_path": row["relative_path"],
                }
                for row in manifest
            ],
            ["canonical_index", "sample_id", "relative_path"],
        )
    for seed in SEEDS:
        split_rows = _read_csv(audit_dir / f"split_manifest_seed{seed}.csv")
        if len(split_rows) != expected_count:
            raise RuntimeError(f"APTOS split seed {seed} does not cover every sample")
        indices = [int(row["canonical_index"]) for row in split_rows]
        if sorted(indices) != list(range(expected_count)):
            raise RuntimeError(f"APTOS split seed {seed} has duplicate or missing indices")
        development_folds = {
            int(row["cv_fold"])
            for row in split_rows
            if row["split"] == "development"
        }
        if development_folds != {0, 1, 2, 3, 4}:
            raise RuntimeError(f"APTOS split seed {seed} does not contain five folds")


def _materialize_features(directory: Path, expected_count: int = 3662) -> Path:
    state = json.loads((directory / "state.json").read_text(encoding="utf-8"))
    if not state.get("completed"):
        raise RuntimeError(f"Extraction is incomplete: {directory}")
    if state.get("success_count") != expected_count or state.get("failure_count") != 0:
        raise RuntimeError(f"Unexpected extraction counts: {directory}")
    samples = _read_csv(directory / "samples.csv")
    if [int(row["row_index"]) for row in samples] != list(range(expected_count)):
        raise RuntimeError(f"Feature/sample row alignment failed: {directory}")
    target = directory / "features.npy"
    expected_shape = (expected_count, int(state["embedding_dim"]))
    if target.is_file():
        values = np.load(target, mmap_mode="r")
        if values.shape != expected_shape or values.dtype != np.float32:
            raise RuntimeError(f"Existing consolidated feature file is invalid: {target}")
        return target
    temporary = directory / "features.tmp.npy"
    output = np.lib.format.open_memmap(
        temporary,
        mode="w+",
        dtype=np.float32,
        shape=expected_shape,
    )
    offset = 0
    for shard in state["shards"]:
        path = directory / shard["file"]
        if _sha256(path) != shard["sha256"]:
            raise RuntimeError(f"Feature shard checksum mismatch: {path}")
        values = np.load(path, mmap_mode="r")
        output[offset : offset + len(values)] = values
        offset += len(values)
    output.flush()
    del output
    if offset != expected_count:
        raise RuntimeError(f"Consolidated feature row count mismatch: {directory}")
    temporary.replace(target)
    if not np.isfinite(np.load(target, mmap_mode="r")).all():
        raise RuntimeError(f"Consolidated features contain NaN or Inf: {target}")
    return target


def _extract_models(
    executable: Path,
    repo: Path,
    audit_dir: Path,
    output_root: Path,
    device: str,
    log_root: Path,
    expected_count: int,
) -> dict[str, tuple[str, Path, str]]:
    extracted: dict[str, tuple[str, Path, str]] = {}
    for model_id, checkpoint_id, batch_size in MODELS:
        output = output_root / f"aptos2019-{model_id}-full"
        _run(
            [
                str(executable),
                "extract",
                checkpoint_id,
                "--manifest",
                str(audit_dir / "manifest.csv"),
                "--path-column",
                "image_path",
                "--id-column",
                "sample_id",
                "--output",
                str(output),
                "--device",
                device,
                "--batch-size",
                str(batch_size),
                "--shard-size",
                "2048",
                "--resume",
            ],
            cwd=repo,
            log=log_root / f"aptos2019-extract-{model_id}.log",
        )
        run_manifest = json.loads((output / "run_manifest.json").read_text(encoding="utf-8"))
        extracted[model_id] = (
            checkpoint_id,
            _materialize_features(output, expected_count),
            str(run_manifest.get("adapter_version") or "unknown"),
        )
    return extracted


def _probe(
    executable: Path,
    repo: Path,
    audit_dir: Path,
    output_root: Path,
    log_root: Path,
    release: str,
    model_id: str,
    checkpoint_id: str,
    features: Path,
    adapter_version: str,
    seed: int,
) -> Path:
    output = output_root / f"aptos2019-{model_id}-probe-seed{seed}"
    if (output / "summary.json").is_file():
        return output
    _run(
        [
            str(executable),
            "benchmark",
            "probe",
            "--features",
            str(features),
            "--samples",
            str(audit_dir / "samples.csv"),
            "--labels",
            str(audit_dir / "labels.csv"),
            "--split-manifest",
            str(audit_dir / f"split_manifest_seed{seed}.csv"),
            "--output",
            str(output),
            "--release",
            release,
            "--model",
            model_id,
            "--checkpoint-id",
            checkpoint_id,
            "--task",
            "aptos2019-dr-5class",
            "--task-name",
            "APTOS 2019 DR 五级分级（去重）",
            "--task-type",
            "ordinal_classification",
            "--label-space",
            "icdr-dr-grade-0-4",
            "--label-semantics",
            "public_aptos2019_icdr_grade",
            "--qualification-status",
            "public_dataset_decontaminated_holdout",
            "--adapter-version",
            adapter_version,
            "--seed",
            str(seed),
        ],
        cwd=repo,
        log=log_root / f"aptos2019-probe-{model_id}-seed{seed}.log",
    )
    return output


def _update_stability(
    main: Path,
    outputs: dict[int, Path],
    adapter_version: str,
) -> None:
    metrics = {
        seed: json.loads((output / "metrics.json").read_text(encoding="utf-8"))
        for seed, output in outputs.items()
    }

    def aggregate(name: str) -> tuple[float, float]:
        values = [float(metrics[seed][name]) for seed in SEEDS]
        return float(np.mean(values)), float(np.std(values, ddof=1))

    manifest_path = main / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["adapter_version"] = adapter_version
    stability: dict[str, Any] = {"seeds": list(SEEDS), "seed_selected_by_test": False}
    for metric in (
        "macro_f1",
        "balanced_accuracy",
        "accuracy",
        "quadratic_weighted_kappa",
    ):
        mean, standard_deviation = aggregate(metric)
        stability[f"{metric}_mean"] = mean
        stability[f"{metric}_std"] = standard_deviation
    manifest["stability"] = stability
    manifest["limitations"] = [
        "使用APTOS 2019公开训练集的本地处理副本；不是Kaggle隐藏测试集。",
        "重复审计后排除标签冲突重复记录并合并同标签副本；去重后按固定种子进行图像级分层85/15划分。",
        "数据不提供patient_id，患者级泄漏无法完全评估，患者级泛化尚未建立。",
    ]
    temporary = manifest_path.with_suffix(".tmp.json")
    temporary.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(manifest_path)
    artifacts = sorted(
        path
        for path in main.iterdir()
        if path.is_file() and path.name != "artifact_manifest.json"
    )
    (main / "artifact_manifest.json").write_text(
        json.dumps(
            {path.name: _sha256(path) for path in artifacts},
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def run(args: argparse.Namespace) -> None:
    audit_dir = args.audit_dir.resolve()
    repo = args.repo.resolve()
    output_root = args.output_root.resolve()
    log_root = args.log_root.resolve()
    audit = _validate_audit(audit_dir)
    expected_count = int(audit["canonical_sample_count"])
    _ensure_probe_inputs(audit_dir, expected_count)
    output_root.mkdir(parents=True, exist_ok=True)
    extracted = _extract_models(
        args.ophbench.resolve(),
        repo,
        audit_dir,
        output_root,
        args.device,
        log_root,
        expected_count,
    )
    jobs = [
        (
            args.ophbench.resolve(),
            repo,
            audit_dir,
            output_root,
            log_root,
            args.release,
            model_id,
            checkpoint_id,
            features,
            adapter_version,
            seed,
        )
        for model_id, (checkpoint_id, features, adapter_version) in extracted.items()
        for seed in SEEDS
    ]
    probe_outputs: dict[tuple[str, int], Path] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(_probe, *job): (job[6], job[10]) for job in jobs}
        for future in concurrent.futures.as_completed(futures):
            probe_outputs[futures[future]] = future.result()
    for model_id, (_checkpoint_id, _features, adapter_version) in extracted.items():
        outputs = {seed: probe_outputs[(model_id, seed)] for seed in SEEDS}
        main = outputs[2026]
        _update_stability(main, outputs, adapter_version)
        _run(
            [
                str(args.ophbench.resolve()),
                "benchmark",
                "import",
                "--release",
                args.release,
                "--model",
                model_id,
                "--task",
                "aptos2019-dr-5class",
                "--metrics",
                str(main / "metrics.json"),
                "--per-class",
                str(main / "per_class.csv"),
                "--run-manifest",
                str(main / "run_manifest.json"),
                "--runs-root",
                str(repo / "benchmark/runs"),
            ],
            cwd=repo,
        )
    _run(
        [
            str(args.ophbench.resolve()),
            "benchmark",
            "build",
            "--release",
            str(repo / f"benchmark/releases/{args.release}.yaml"),
            "--runs-root",
            str(repo / "benchmark/runs"),
            "--output",
            str(repo / "benchmark/generated"),
        ],
        cwd=repo,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-dir", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--ophbench", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--log-root", type=Path, required=True)
    parser.add_argument("--release", default="2026.07")
    parser.add_argument("--device", default="cuda:0")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
