from __future__ import annotations

import hashlib
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable

from .dataset import open_rgb_image
from .manifest import load_manifest, scan_directory, serialized_manifest, sha256_file, write_input_manifest
from .resume import load_state, save_state
from .schemas import ExtractionConfig, ExtractionResult
from .validation import validate_embeddings
from .writer import atomic_json, sha256_file as artifact_sha256, write_csv


class ExtractionError(RuntimeError):
    pass


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _fingerprint(config: ExtractionConfig, checkpoint_sha256: str, input_sha256: str, adapter) -> dict:
    return {
        "model_id": config.model_id,
        "checkpoint_id": config.checkpoint_id,
        "checkpoint_sha256": checkpoint_sha256,
        "adapter_version": getattr(adapter, "adapter_version", "unknown"),
        "preprocessing_id": getattr(adapter, "preprocessing_id", "adapter-default"),
        "input_manifest_sha256": input_sha256,
        "batch_size": config.batch_size,
        "shard_size": config.shard_size,
    }


def _prepare_output(config: ExtractionConfig, fingerprint: dict) -> dict | None:
    output = config.output_dir
    state = load_state(output) if output.exists() else None
    if state is not None:
        if state.get("fingerprint") != fingerprint:
            raise ExtractionError("Output directory belongs to a different extraction fingerprint")
        if state.get("completed"):
            return state
        if not config.resume:
            raise ExtractionError("Extraction is incomplete; re-run with --resume")
        return state
    if output.exists() and {item.name for item in output.iterdir()} - {"input_manifest.csv"}:
        raise ExtractionError("Refusing to write into a non-empty directory without OphBench state.json")
    output.mkdir(parents=True, exist_ok=True)
    (output / "features").mkdir(exist_ok=True)
    return None


def _flush_shard(output: Path, shard_index: int, chunks, sample_rows):
    import numpy as np

    array = np.concatenate(chunks, axis=0).astype("float32", copy=False)
    filename = f"shard-{shard_index:05d}.npy"
    target = output / "features" / filename
    temporary = target.with_suffix(".tmp.npy")
    np.save(temporary, array)
    temporary.replace(target)
    for offset, row in enumerate(sample_rows):
        row.update({"shard": filename, "offset": offset, "status": "success"})
    return array.shape[1], filename


def run_extraction(
    config: ExtractionConfig,
    adapter_factory: Callable[..., object] | None = None,
) -> ExtractionResult:
    """Run a local, frozen image encoder without downloading assets or mutating inputs."""
    if (config.input_dir is None) == (config.manifest is None):
        raise ExtractionError("Exactly one of input_dir or manifest must be provided")
    if config.batch_size < 1 or config.shard_size < 1:
        raise ExtractionError("batch_size and shard_size must be positive")
    if not config.checkpoint.is_file():
        raise ExtractionError("checkpoint must be an existing local file")

    existing_state = load_state(config.output_dir) if config.output_dir.exists() else None
    if config.output_dir.exists() and any(config.output_dir.iterdir()) and existing_state is None:
        raise ExtractionError("Refusing to write into a non-empty directory without OphBench state.json")

    records = (
        scan_directory(config.input_dir) if config.input_dir else load_manifest(config.manifest, config.path_column, config.id_column)
    )
    identifiers = [record["sample_id"] for record in records]
    if len(identifiers) != len(set(identifiers)):
        raise ExtractionError("Input manifest has duplicate sample_id values")
    input_sha256 = hashlib.sha256(serialized_manifest(records)).hexdigest()
    if adapter_factory is None:
        from ophbench.models.factory import load_adapter

        adapter_factory = load_adapter
    adapter = adapter_factory(
        model_id=config.model_id,
        checkpoint_id=config.checkpoint_id,
        checkpoint_path=config.checkpoint,
        device=config.device,
    )
    adapter.load()
    import torch

    model = getattr(adapter, "model", None)
    if model is not None:
        model.eval()
        model.requires_grad_(False)
        if any(parameter.requires_grad for parameter in model.parameters()):
            raise ExtractionError("Adapter model still has trainable parameters after freezing")

    checkpoint_sha256 = sha256_file(config.checkpoint)
    fingerprint = _fingerprint(config, checkpoint_sha256, input_sha256, adapter)
    state = _prepare_output(config, fingerprint)
    if state and state.get("completed"):
        return ExtractionResult(config.output_dir, state["success_count"], state["failure_count"], state["embedding_dim"], True)
    written_input_sha256 = write_input_manifest(records, config.output_dir / "input_manifest.csv")
    if written_input_sha256 != input_sha256:
        raise ExtractionError("Input manifest serialization changed during extraction setup")

    state = state or {"processed": 0, "success_rows": [], "failures": [], "shards": [], "started_at": _now()}
    processed = state["processed"]
    success_rows = state["success_rows"]
    failures = state["failures"]
    shards = state["shards"]
    shard_chunks, shard_rows = [], []
    shard_index = len(shards)
    embedding_dim = state.get("embedding_dim")

    def persist(completed: bool = False):
        save_state(
            config.output_dir,
            fingerprint=fingerprint,
            processed=processed,
            success_rows=success_rows,
            failures=failures,
            shards=shards,
            embedding_dim=embedding_dim,
            success_count=len(success_rows),
            failure_count=len(failures),
            started_at=state["started_at"],
            completed=completed,
        )

    def flush_pending_shard(force: bool = False):
        nonlocal embedding_dim, shard_index, shard_chunks, shard_rows
        if not shard_chunks or (not force and sum(len(chunk) for chunk in shard_chunks) < config.shard_size):
            return
        dim, filename = _flush_shard(config.output_dir, shard_index, shard_chunks, shard_rows)
        embedding_dim = embedding_dim or dim
        shards.append({"file": f"features/{filename}", "sample_count": len(shard_rows), "shape": [len(shard_rows), dim]})
        success_rows.extend(shard_rows)
        shard_index += 1
        shard_chunks, shard_rows = [], []

    pending: list[tuple[dict, object]] = []

    def encode_pending():
        nonlocal embedding_dim, shard_index, shard_chunks, shard_rows
        if not pending:
            return
        try:
            tensors = [adapter.preprocess(image) for _, image in pending]
            batch = torch.stack(tensors)
            with torch.inference_mode():
                embeddings = adapter.encode_image(batch)
            validate_embeddings(embeddings)
            values = embeddings.detach().cpu().numpy()
            if len(values) != len(pending):
                raise ValueError("Adapter output batch size does not match input batch size")
            embedding_dim = embedding_dim or int(values.shape[1])
            if values.shape[1] != embedding_dim:
                raise ValueError("Embedding dimension changed during one extraction run")
            shard_chunks.append(values)
            shard_rows.extend({"row_index": len(success_rows) + len(shard_rows), "sample_id": record["sample_id"], "relative_path": record["relative_path"]} for record, _ in pending)
        except Exception as exc:  # isolate a bad sample, then retain other samples
            if len(pending) == 1:
                record, _ = pending[0]
                failures.append({"sample_id": record["sample_id"], "relative_path": record["relative_path"], "failure_stage": "preprocess_or_encode", "exception_type": type(exc).__name__, "sanitized_error": str(exc)[:300]})
            else:
                items = list(pending)
                pending.clear()
                for item in items:
                    pending.append(item)
                    encode_pending()
                return
        pending.clear()
        if sum(len(chunk) for chunk in shard_chunks) >= config.shard_size:
            flush_pending_shard()
            persist()

    for record in records[processed:]:
        processed += 1
        try:
            image = open_rgb_image(record["source_path"])
        except Exception as exc:
            failures.append({"sample_id": record["sample_id"], "relative_path": record["relative_path"], "failure_stage": "image_decode", "exception_type": type(exc).__name__, "sanitized_error": str(exc)[:300]})
            flush_pending_shard(force=True)
            persist()
            continue
        pending.append((record, image))
        if len(pending) >= config.batch_size:
            encode_pending()
    encode_pending()
    flush_pending_shard(force=True)
    if embedding_dim is None and records:
        raise ExtractionError("No readable images produced valid embeddings")
    write_csv(config.output_dir / "samples.csv", success_rows, ["row_index", "sample_id", "relative_path", "shard", "offset", "status"])
    write_csv(config.output_dir / "failures.csv", failures, ["sample_id", "relative_path", "failure_stage", "exception_type", "sanitized_error"])
    for shard in shards:
        shard["sha256"] = artifact_sha256(config.output_dir / shard["file"])
    artifacts = ["input_manifest.csv", "samples.csv", "failures.csv"] + [item["file"] for item in shards]
    artifact_manifest = {name: artifact_sha256(config.output_dir / name) for name in artifacts}
    atomic_json(config.output_dir / "artifact_manifest.json", artifact_manifest)
    summary = {"success_count": len(success_rows), "failure_count": len(failures), "embedding_dim": embedding_dim, "completed_at": _now()}
    atomic_json(config.output_dir / "extraction_summary.json", summary)
    from ophbench._version import __version__

    run_manifest = {**fingerprint, **summary, "model_id": config.model_id, "checkpoint_id": config.checkpoint_id, "dtype": "float32", "device": config.device, "batch_size": config.batch_size, "sample_count": len(records), "git_commit": _git_commit(), "package_version": __version__}
    atomic_json(config.output_dir / "run_manifest.json", run_manifest)
    persist(completed=True)
    return ExtractionResult(config.output_dir, len(success_rows), len(failures), embedding_dim or 0, True)
