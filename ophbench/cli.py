from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .registry.builder import build_catalog
from .registry.importer import import_seed
from .registry.loader import load_registry
from .registry.validator import RegistryValidationError, validate_registry

app = typer.Typer(help="Ophthalmic foundation model registry tools.")
registry_app = typer.Typer()
catalog_app = typer.Typer()
app.add_typer(registry_app, name="registry")
app.add_typer(catalog_app, name="catalog")
console = Console()


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
