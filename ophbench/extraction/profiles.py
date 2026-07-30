from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from ophbench.api import load_registry

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "ophbench" / "config.yaml"


@dataclass(frozen=True)
class ResolvedExtractionProfile:
    model_id: str
    checkpoint_id: str
    checkpoint_path: Path
    config_path: Path | None


def load_extraction_defaults(config_path: Path | None = None) -> tuple[dict[str, Any], Path | None]:
    """Load explicit or per-user local defaults without downloading any assets."""

    selected = config_path
    if selected is None:
        configured = os.environ.get("OPHBENCH_CONFIG")
        selected = Path(configured).expanduser() if configured else DEFAULT_CONFIG_PATH
        if not selected.is_file():
            return {}, None
    selected = selected.expanduser().resolve()
    payload = yaml.safe_load(selected.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Extraction config must contain a YAML mapping: {selected}")
    return payload, selected


def _profile_checkpoint_id(profile: str, values: dict[str, Any]) -> str:
    aliases = values.get("aliases") or {}
    if not isinstance(aliases, dict):
        raise ValueError("Extraction config field 'aliases' must be a mapping")
    requested = str(aliases.get(profile, profile))
    snapshot = load_registry()
    by_checkpoint = {item.checkpoint_id: item for item in snapshot.checkpoints}
    if requested in by_checkpoint:
        return requested
    candidates = [item.checkpoint_id for item in snapshot.checkpoints if item.model_id == requested]
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise ValueError(f"Unknown extraction profile: {profile}")
    choices = ", ".join(sorted(candidates))
    raise ValueError(f"Profile '{profile}' is ambiguous; choose one checkpoint: {choices}")


def _configured_checkpoint_path(
    checkpoint_id: str,
    values: dict[str, Any],
) -> Path | None:
    checkpoints = values.get("checkpoints") or {}
    if not isinstance(checkpoints, dict):
        raise ValueError("Extraction config field 'checkpoints' must be a mapping")
    configured = checkpoints.get(checkpoint_id)
    if configured:
        return Path(str(configured)).expanduser()
    environment_name = (
        f"OPHBENCH_CHECKPOINT_{checkpoint_id.upper().replace('-', '_').replace('.', '_')}"
    )
    environment_value = os.environ.get(environment_name)
    return Path(environment_value).expanduser() if environment_value else None


def resolve_extraction_profile(
    *,
    profile: str | None,
    model_id: str | None,
    checkpoint_id: str | None,
    checkpoint_path: Path | None,
    values: dict[str, Any],
    config_path: Path | None,
) -> ResolvedExtractionProfile:
    """Resolve the short profile syntax while preserving explicit legacy arguments."""

    if profile:
        resolved_checkpoint_id = _profile_checkpoint_id(profile, values)
        if checkpoint_id and checkpoint_id != resolved_checkpoint_id:
            raise ValueError(
                f"Profile '{profile}' resolves to {resolved_checkpoint_id}, not {checkpoint_id}"
            )
        checkpoint_id = resolved_checkpoint_id
    checkpoint_id = checkpoint_id or values.get("checkpoint_id")
    model_id = model_id or values.get("model")
    if not checkpoint_id:
        raise ValueError("Provide a profile or --checkpoint-id")

    snapshot = load_registry()
    record = next(
        (item for item in snapshot.checkpoints if item.checkpoint_id == checkpoint_id),
        None,
    )
    if record is None:
        raise ValueError(f"Unknown checkpoint-id: {checkpoint_id}")
    if model_id and model_id != record.model_id:
        raise ValueError(
            f"Checkpoint {checkpoint_id} belongs to model {record.model_id}, not {model_id}"
        )
    model_id = record.model_id

    legacy_checkpoint = values.get("checkpoint")
    resolved_path = (
        checkpoint_path
        or (Path(str(legacy_checkpoint)).expanduser() if legacy_checkpoint else None)
        or _configured_checkpoint_path(checkpoint_id, values)
    )
    if resolved_path is None:
        location = config_path or DEFAULT_CONFIG_PATH
        raise ValueError(
            f"No local path configured for {checkpoint_id}. Add it under "
            f"'checkpoints' in {location} or pass --checkpoint."
        )
    resolved_path = resolved_path.resolve()
    if not resolved_path.is_file():
        raise ValueError(f"Configured checkpoint does not exist: {resolved_path}")
    return ResolvedExtractionProfile(
        model_id=model_id,
        checkpoint_id=checkpoint_id,
        checkpoint_path=resolved_path,
        config_path=config_path,
    )
