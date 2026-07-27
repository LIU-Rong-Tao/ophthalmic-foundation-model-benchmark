from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Task:
    task_id: str
    task_type: str
    modality: str
    dataset_display_name: str
    class_count: int
    sample_count: int | None
    split_level: str
    patient_id_available: bool
    label_semantics: str
    primary_metric: str


@dataclass(frozen=True)
class ModelRun:
    run_id: str
    release_id: str
    model_id: str
    checkpoint_id: str
    adapter_version: str | None
    protocol_id: str
    task_id: str
    qualification_status: str
    metrics: dict[str, Any]
    cost: dict[str, Any]
    artifacts: dict[str, str]
    limitations: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
