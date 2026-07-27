"""Public, installation-safe registry consumer API."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

import yaml

from .registry.loader import load_registry as _load_registry_from_path
from .registry.schemas import CheckpointRecord, ModelRecord

from ._version import __version__


@dataclass(frozen=True)
class RegistrySnapshot:
    """Immutable snapshot of validated model and checkpoint records."""

    models: tuple[ModelRecord, ...]
    checkpoints: tuple[CheckpointRecord, ...]
    package_version: str
    schema_version: str
    registry_source: str

    @property
    def model_count(self) -> int:
        """Number of model records in the snapshot."""

        return len(self.models)

    @property
    def checkpoint_count(self) -> int:
        """Number of checkpoint records in the snapshot."""

        return len(self.checkpoints)


def _load_resource_records(directory: resources.abc.Traversable, record_type):
    records = []
    for item in sorted(directory.iterdir(), key=lambda entry: entry.name):
        if item.name.endswith(".yaml"):
            records.append(record_type.model_validate(yaml.safe_load(item.read_text(encoding="utf-8"))))
    return records


def _schema_version(models: Iterable[ModelRecord], checkpoints: Iterable[CheckpointRecord]) -> str:
    records = [*models, *checkpoints]
    versions = {record.schema_version for record in records}
    if len(versions) != 1:
        raise ValueError(f"Registry contains inconsistent schema versions: {sorted(versions)}")
    return versions.pop()


def load_registry(registry_root: Path | str | None = None) -> RegistrySnapshot:
    """Load the packaged registry or an explicit development registry root."""

    if registry_root is None:
        root = resources.files("ophbench").joinpath("_registry_data")
        models = _load_resource_records(root.joinpath("models"), ModelRecord)
        checkpoints = _load_resource_records(root.joinpath("checkpoints"), CheckpointRecord)
        source = "package:ophbench/_registry_data"
    else:
        explicit_root = Path(registry_root).expanduser().resolve()
        models, checkpoints = _load_registry_from_path(explicit_root)
        source = str(explicit_root)
    return RegistrySnapshot(
        models=tuple(models),
        checkpoints=tuple(checkpoints),
        package_version=__version__,
        schema_version=_schema_version(models, checkpoints),
        registry_source=source,
    )


def get_registry_info(registry_root: Path | str | None = None) -> RegistrySnapshot:
    """Return registry metadata and records as a stable snapshot."""

    return load_registry(registry_root)


def list_models(registry_root: Path | str | None = None) -> tuple[ModelRecord, ...]:
    """List all registered models in deterministic order."""

    return load_registry(registry_root).models


def list_checkpoints(
    model_id: str | None = None,
    registry_root: Path | str | None = None,
) -> tuple[CheckpointRecord, ...]:
    """List checkpoints, optionally restricted to one model ID."""

    checkpoints = load_registry(registry_root).checkpoints
    if model_id is None:
        return checkpoints
    return tuple(checkpoint for checkpoint in checkpoints if checkpoint.model_id == model_id)
