from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .registry.builder import build_catalog
from .registry.importer import import_seed
from .registry.loader import load_registry
from .registry.validator import RegistryValidationError, validate_registry
from .extraction import ExtractionConfig, ExtractionError, run_extraction
from .benchmark import build_benchmark, import_benchmark_run

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
    model: str = typer.Option(None, "--model"),
    checkpoint_id: str = typer.Option(None, "--checkpoint-id"),
    checkpoint: Path = typer.Option(None, "--checkpoint"),
    output_dir: Path = typer.Option(None, "--output-dir"),
    input_dir: Path = typer.Option(None, "--input-dir"),
    manifest: Path = typer.Option(None, "--manifest"),
    path_column: str = typer.Option("image_path", "--path-column"),
    id_column: str = typer.Option("sample_id", "--id-column"),
    device: str = typer.Option("cpu", "--device"),
    batch_size: int = typer.Option(32, "--batch-size"),
    num_workers: int = typer.Option(0, "--num-workers"),
    shard_size: int = typer.Option(2048, "--shard-size"),
    resume: bool = typer.Option(False, "--resume"),
    config: Path = typer.Option(None, "--config", exists=True),
):
    """以一条命令生成可恢复的冻结特征分片。"""
    if config:
        import yaml

        values = yaml.safe_load(config.read_text(encoding="utf-8")) or {}
        model, checkpoint_id = model or values.get("model"), checkpoint_id or values.get("checkpoint_id")
        checkpoint = checkpoint or (Path(values["checkpoint"]) if values.get("checkpoint") else None)
        output_dir = output_dir or (Path(values["output_dir"]) if values.get("output_dir") else None)
        input_dir = input_dir or (Path(values["input_dir"]) if values.get("input_dir") else None)
        manifest = manifest or (Path(values["manifest"]) if values.get("manifest") else None)
        path_column, id_column = values.get("path_column", path_column), values.get("id_column", id_column)
        device, batch_size = values.get("device", device), values.get("batch_size", batch_size)
    if num_workers:
        console.print("--num-workers is accepted but v0.3 currently performs safe synchronous decoding.", style="yellow")
    if not all((model, checkpoint_id, checkpoint, output_dir)):
        raise typer.BadParameter("model, checkpoint-id, checkpoint, and output-dir are required")
    try:
        result = run_extraction(
            ExtractionConfig(
                model_id=model,
                checkpoint_id=checkpoint_id,
                checkpoint=checkpoint,
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
    console.print(f"Extraction complete: {result.success_count} success, {result.failure_count} failures, dim={result.embedding_dim}.")


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
    command = [sys.executable, "-m", "streamlit", "run", str(script), "--server.address", host, "--server.port", str(port), "--", str(results)]
    raise typer.Exit(subprocess.call(command))


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
        f"Catalog {state}: {result.model_count} models, "
        f"{result.checkpoint_count} checkpoints."
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
