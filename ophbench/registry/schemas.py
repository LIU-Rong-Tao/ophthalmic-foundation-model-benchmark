from __future__ import annotations

from typing import Literal
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, field_validator

PublicationType = Literal["journal", "conference", "preprint", "unknown"]
VerificationStatus = Literal["seed_unverified", "partially_verified", "verified", "blocked"]
RuntimePhase = Literal[
    "phase1_image_encoder", "phase1_specialized", "phase2_vision_language", "catalog_only"
]
AdapterStatus = Literal["not_started", "scaffolded", "implemented", "failed"]
RunStatus = Literal["not_run", "passed", "failed", "blocked"]
AccessType = Literal[
    "open", "auth_required", "gated", "application_required", "api_only", "unavailable", "unknown"
]
Provider = Literal[
    "huggingface",
    "google_drive",
    "github_release",
    "zenodo",
    "official_repository",
    "other",
    "unknown",
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Provenance(StrictModel):
    source_file: str
    source_sheet: str
    source_row: int
    imported_at: str


class ImplementationStatus(StrictModel):
    adapter_status: AdapterStatus
    smoke_test_status: RunStatus
    benchmark_status: RunStatus


def _validate_url(value: str | None) -> str | None:
    if value is None:
        return value
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("URL must use http or https")
    return value


class ModelRecord(StrictModel):
    schema_version: Literal["1.0"]
    model_id: str
    model_name: str
    year: int | None
    publication_type: PublicationType
    venue: str
    model_category: str
    modalities: list[str]
    architecture: str
    pretraining_data_summary: str
    pretraining_strategy: str
    reported_summary: str
    paper_url: str | None
    code_url: str | None
    code_available: bool
    capabilities: list[str]
    benchmark_tracks: list[str]
    runtime_phase: RuntimePhase
    license: str | None
    license_verified: bool
    verification_status: VerificationStatus
    implementation: ImplementationStatus
    reported_tasks_text: str
    provenance: Provenance
    notes: list[str]

    _paper_url = field_validator("paper_url")(_validate_url)
    _code_url = field_validator("code_url")(_validate_url)


class CheckpointRecord(StrictModel):
    schema_version: Literal["1.0"]
    checkpoint_id: str
    model_id: str
    checkpoint_name: str
    modalities: list[str]
    weight_url: str | None
    provider: Provider
    access_type: AccessType
    requires_auth: bool
    redistribution_allowed: Literal["yes", "no", "unknown"]
    license: str | None
    framework: str | None
    input_size: str | None
    normalization: str | None
    embedding_dim: int | None
    sha256: str | None
    source_commit: str | None
    verification_status: VerificationStatus
    last_verified: str | None
    provenance: Provenance
    notes: list[str]

    _weight_url = field_validator("weight_url")(_validate_url)
