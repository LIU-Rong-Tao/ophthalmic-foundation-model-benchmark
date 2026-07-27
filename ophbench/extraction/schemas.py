from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExtractionConfig:
    model_id: str
    checkpoint_id: str
    checkpoint: Path
    output_dir: Path
    input_dir: Path | None = None
    manifest: Path | None = None
    path_column: str = "image_path"
    id_column: str = "sample_id"
    device: str = "cpu"
    batch_size: int = 32
    shard_size: int = 2048
    resume: bool = False


@dataclass(frozen=True)
class ExtractionResult:
    output_dir: Path
    success_count: int
    failure_count: int
    embedding_dim: int
    completed: bool
