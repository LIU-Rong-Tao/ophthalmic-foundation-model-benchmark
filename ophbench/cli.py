from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .benchmark import build_benchmark, import_benchmark_run
from .extraction import ExtractionConfig, ExtractionError, run_extraction
from .extraction.profiles import load_extraction_defaults, resolve_extraction_profile
from .registry.builder import build_catalog
from .registry.importer import import_seed
from .registry.loader import load_registry
from .registry.validator import RegistryValidationError, validate_registry

app = typer.Typer(help="Ophthalmic foundation model registry tools.")
registry_app = typer.Typer()
catalog_app = typer.Typer()
benchmark_app = typer.Typer()
app.add_typer(registry_app, name="registry")
app.add_typer(catalog_app, name="catalog")
app.add_typer(benchmark_app, name="benchmark")
console = Console()


@app.command("extract")
def extract_command(
    profile: str | None = typer.Argument(
        None,
        help="Checkpoint profile, for example retfound-cfp, retfound-green, or eyeclip.",
    ),
    model: str | None = typer.Option(None, "--model"),
    checkpoint_id: str | None = typer.Option(None, "--checkpoint-id"),
    checkpoint: Path | None = typer.Option(None, "--checkpoint"),
    output_dir: Path | None = typer.Option(None, "--output", "--output-dir"),
    input_dir: Path | None = typer.Option(None, "--input", "--input-dir"),
    manifest: Path | None = typer.Option(None, "--manifest"),
    path_column: str = typer.Option("image_path", "--path-column"),
    id_column: str = typer.Option("sample_id", "--id-column"),
    device: str | None = typer.Option(None, "--device"),
    batch_size: int | None = typer.Option(None, "--batch-size"),
    num_workers: int | None = typer.Option(None, "--num-workers"),
    shard_size: int | None = typer.Option(None, "--shard-size"),
    resume: bool = typer.Option(False, "--resume"),
    config: Path | None = typer.Option(None, "--config", exists=True),
):
    """以一条命令生成可恢复的冻结特征分片；不下载权重或上传数据。"""
    try:
        values, loaded_config = load_extraction_defaults(config)
        resolved = resolve_extraction_profile(
            profile=profile,
            model_id=model,
            checkpoint_id=checkpoint_id,
            checkpoint_path=checkpoint,
            values=values,
            config_path=loaded_config,
        )
    except (OSError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    output_dir = output_dir or (
        Path(str(values["output_dir"])).expanduser() if values.get("output_dir") else None
    )
    input_dir = input_dir or (
        Path(str(values["input_dir"])).expanduser() if values.get("input_dir") else None
    )
    manifest = manifest or (
        Path(str(values["manifest"])).expanduser() if values.get("manifest") else None
    )
    path_column = str(values.get("path_column", path_column))
    id_column = str(values.get("id_column", id_column))
    device = device or str(values.get("device", "cpu"))
    batch_size = batch_size if batch_size is not None else int(values.get("batch_size", 32))
    num_workers = num_workers if num_workers is not None else int(values.get("num_workers", 0))
    shard_size = shard_size if shard_size is not None else int(values.get("shard_size", 2048))
    if num_workers:
        console.print(
            "--num-workers is accepted but v0.3 currently performs safe synchronous decoding.",
            style="yellow",
        )
    if output_dir is None:
        raise typer.BadParameter("--output/--output-dir is required")
    try:
        result = run_extraction(
            ExtractionConfig(
                model_id=resolved.model_id,
                checkpoint_id=resolved.checkpoint_id,
                checkpoint=resolved.checkpoint_path,
                output_dir=output_dir,
                input_dir=input_dir,
                manifest=manifest,
                path_column=path_column,
                id_column=id_column,
                device=device,
                batch_size=batch_size,
                shard_size=shard_size,
                resume=resume,
            )
        )
    except (ExtractionError, ValueError, OSError) as exc:
        console.print(f"Extraction failed: {exc}", style="red")
        raise typer.Exit(1) from exc
    console.print(
        f"Extraction complete: {result.success_count} success, "
        f"{result.failure_count} failures, dim={result.embedding_dim}."
    )


@benchmark_app.command("import")
def benchmark_import_command(
    release: str = typer.Option(..., "--release"),
    model: str = typer.Option(..., "--model"),
    task: str = typer.Option(..., "--task"),
    metrics: Path = typer.Option(..., "--metrics", exists=True),
    per_class: Path | None = typer.Option(None, "--per-class", exists=True),
    run_manifest: Path | None = typer.Option(None, "--run-manifest", exists=True),
    runs_root: Path = typer.Option(Path("benchmark/runs"), "--runs-root"),
):
    output = import_benchmark_run(
        release_id=release,
        model_id=model,
        task_id=task,
        metrics_path=metrics,
        per_class_path=per_class,
        run_manifest_path=run_manifest,
        runs_root=runs_root,
    )
    console.print(f"Imported sanitized benchmark run: {output}")


@benchmark_app.command("build")
def benchmark_build_command(
    release: Path = typer.Option(..., "--release", exists=True),
    runs_root: Path = typer.Option(Path("benchmark/runs"), "--runs-root"),
    output: Path = typer.Option(Path("benchmark/generated"), "--output"),
):
    result = build_benchmark(release, runs_root, output)
    console.print(f"Built {result['run_count']} dashboard run(s) for {result['release_id']}.")


@benchmark_app.command("probe")
def benchmark_probe_command(
    features: Path = typer.Option(..., "--features", exists=True),
    samples: Path = typer.Option(..., "--samples", exists=True),
    labels: Path = typer.Option(..., "--labels", exists=True),
    split_manifest: Path = typer.Option(..., "--split-manifest", exists=True),
    output: Path = typer.Option(..., "--output"),
    release: str = typer.Option(..., "--release"),
    model: str = typer.Option(..., "--model"),
    checkpoint_id: str = typer.Option(..., "--checkpoint-id"),
    task: str = typer.Option(..., "--task"),
    task_name: str | None = typer.Option(None, "--task-name"),
    label_space: str | None = typer.Option(None, "--label-space"),
    adapter_version: str | None = typer.Option(None, "--adapter-version"),
    seed: int = typer.Option(2026, "--seed"),
):
    """对已冻结且严格对齐的特征运行统一多分类轻量探针。"""
    from .evaluation import PrecomputedProbeConfig, run_precomputed_probe

    result = run_precomputed_probe(
        PrecomputedProbeConfig(
            features=features,
            samples=samples,
            labels=labels,
            split_manifest=split_manifest,
            output_dir=output,
            release_id=release,
            model_id=model,
            checkpoint_id=checkpoint_id,
            task_id=task,
            task_display_name=task_name,
            label_space=label_space,
            adapter_version=adapter_version,
            seed=seed,
        )
    )
    console.print(f"Built frozen-feature probe artifacts: {result}")


@app.command("dashboard")
def dashboard_command(
    results: Path = typer.Option(Path("benchmark/generated"), "--results"),
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8501, "--port"),
):
    """用 Streamlit 启动只读的本地结果展示页。"""
    import subprocess
    import sys

    script = Path(__file__).with_name("dashboard.py")
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(script),
        "--server.address",
        host,
        "--server.port",
        str(port),
    ]
    environment = {**__import__("os").environ, "OPHBENCH_DASHBOARD_RESULTS": str(results.resolve())}
    raise typer.Exit(subprocess.call(command, env=environment))


@registry_app.command("import-seed")
def import_seed_command(input: Path = typer.Option(..., exists=True)):
    result = import_seed(input)
    console.print(
        f"Imported {result.model_count} models and {result.checkpoint_count} checkpoints."
    )


@registry_app.command("validate")
def validate_command(
    online: bool = typer.Option(False, help="Check URL reachability without modifying records."),
):
    try:
        models, checkpoints, warnings = validate_registry(online=online)
    except (RegistryValidationError, ValueError) as exc:
        console.print(f"Validation failed: {exc}", style="red")
        raise typer.Exit(1) from exc
    console.print(f"Valid registry: {len(models)} models, {len(checkpoints)} checkpoints.")
    for warning in warnings:
        console.print(f"WARNING: {warning}", style="yellow")


@catalog_app.command("build")
def build_command(check: bool = typer.Option(False)):
    result = build_catalog(
        Path("registry"), Path("catalog"), check=check, model_zoo_path=Path("MODEL_ZOO.md")
    )
    if result.is_stale:
        console.print("Generated catalog is stale.", style="red")
        raise typer.Exit(1)
    state = "is current" if check else "built"
    console.print(
        f"Catalog {state}: {result.model_count} models, {result.checkpoint_count} checkpoints."
    )


@app.command("list-models")
def list_models():
    models, _ = load_registry(Path("registry"))
    table = Table("Model ID", "Name", "Modalities", "Runtime phase", "Adapter")
    for model in sorted(models, key=lambda x: x.model_id):
        table.add_row(
            model.model_id,
            model.model_name,
            ", ".join(model.modalities),
            model.runtime_phase,
            model.implementation.adapter_status,
        )
    console.print(table)


def _find_model(model_id):
    models, checkpoints = load_registry(Path("registry"))
    model = next((item for item in models if item.model_id == model_id), None)
    if not model:
        console.print(f"Unknown model: {model_id}", style="red")
        raise typer.Exit(1)
    return model, [cp for cp in checkpoints if cp.model_id == model_id]


@app.command("show-model")
def show_model(model_id: str):
    model, checkpoints = _find_model(model_id)
    console.print_json(
        data={
            **model.model_dump(mode="json"),
            "checkpoints": [c.model_dump(mode="json") for c in checkpoints],
        }
    )


@app.command("doctor")
def doctor(model: str = typer.Option(..., "--model")):
    record, checkpoints = _find_model(model)
    warnings = []
    if not record.license_verified:
        warnings.append("Model license has not been verified.")
    if record.implementation.adapter_status != "implemented":
        warnings.append("No implemented adapter is registered in v0.1.")
    if any(cp.requires_auth for cp in checkpoints):
        warnings.append("At least one checkpoint requires authentication.")
    report = {
        "model_exists": True,
        "model_id": record.model_id,
        "checkpoint_count": len(checkpoints),
        "weight_access": sorted({cp.access_type for cp in checkpoints}),
        "requires_auth": any(cp.requires_auth for cp in checkpoints),
        "license_verified": record.license_verified,
        "adapter_status": record.implementation.adapter_status,
        "smoke_test_status": record.implementation.smoke_test_status,
        "benchmark_status": record.implementation.benchmark_status,
        "runtime_phase": record.runtime_phase,
        "warnings": warnings,
    }
    console.print_json(data=report)
