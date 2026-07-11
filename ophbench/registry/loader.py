from pathlib import Path

import yaml

from .schemas import CheckpointRecord, ModelRecord


def load_yaml_records(directory: Path, record_type):
    return [
        record_type.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
        for path in sorted(directory.glob("*.yaml"))
    ]


def load_registry(root: Path):
    return (
        load_yaml_records(root / "models", ModelRecord),
        load_yaml_records(root / "checkpoints", CheckpointRecord),
    )
