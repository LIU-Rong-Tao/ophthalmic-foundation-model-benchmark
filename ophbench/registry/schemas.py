from __future__ import annotations

from typing import Annotated, Literal
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

PublicationType = Literal["journal", "conference", "preprint", "unknown"]
VerificationStatus = Literal["seed_unverified", "partially_verified", "verified", "blocked"]
RuntimePhase = Literal[
    "phase1_image_encoder", "phase1_specialized", "phase2_vision_language", "catalog_only"
]
AdapterStatus = Literal["not_started", "scaffolded", "implemented", "failed"]
RunStatus = Literal["not_run", "passed", "failed", "blocked"]
EvidenceStatus = Literal["pending", "verified", "blocked", "not_applicable"]
AccessType = Literal[
    "open", "auth_required", "gated", "application_required", "api_only", "unavailable", "unknown"
]
ArtifactType = Literal[
    "foundation_encoder",
    "vision_language_model",
    "task_checkpoint",
    "generative_model",
    "ablation_checkpoint",
    "multimodal_full_model",
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
Identifier = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    ),
]
CheckpointIdentifier = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*(?:\.[0-9]+)?$",
    ),
]
NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Modality = Literal[
    "CFP",
    "OCT",
    "OCTA",
    "FFA",
    "SLO",
    "ICGA",
    "FAF",
    "ultrasound",
    "external_eye",
    "slit_lamp",
    "specular_microscopy",
    "corneal_photography",
    "MRI",
    "UBM",
    "CT",
    "RetCam",
    "PET",
    "X_ray",
    "text",
    "retinal_layer_pseudolabels",
    "other",
]
Capability = Literal[
    "image_encoding",
    "feature_extraction",
    "classification",
    "risk_prediction",
    "prognosis",
    "segmentation",
    "detection",
    "keypoint_localization",
    "zero_shot_classification",
    "few_shot_classification",
    "retrieval",
    "multimodal_alignment",
    "vqa",
    "report_generation",
    "uncertainty_estimation",
    "ood_detection",
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Provenance(StrictModel):
    source_file: NonEmptyStr
    source_sheet: NonEmptyStr
    source_row: int
    imported_at: str


class ImplementationStatus(StrictModel):
    adapter_status: AdapterStatus
    smoke_test_status: RunStatus
    benchmark_status: RunStatus


class VerificationBreakdown(StrictModel):
    paper: EvidenceStatus = "pending"
    code: EvidenceStatus = "pending"
    checkpoint_url: EvidenceStatus = "pending"
    checkpoint_file: EvidenceStatus = "pending"
    license: EvidenceStatus = "pending"
    preprocessing: EvidenceStatus = "pending"
    adapter: EvidenceStatus = "pending"
    feature_output: EvidenceStatus = "pending"


class ArchitectureDetails(StrictModel):
    encoder_family: str | None = None
    encoder_variant: str | None = None
    patch_size: int | None = None
    pretraining_objective: str | None = None
    runtime_component: str | None = None


class InputSpec(StrictModel):
    color_space: str | None = None
    size: tuple[int, int] | None = None


class ResizeSpec(StrictModel):
    size: tuple[int, int] | None = None
    interpolation: str | None = None


class CropSpec(StrictModel):
    type: str | None = None
    size: tuple[int, int] | None = None


class NormalizationSpec(StrictModel):
    mean: tuple[float, ...]
    std: tuple[float, ...]


class PreprocessingSpec(StrictModel):
    resize: ResizeSpec | None = None
    crop: CropSpec | None = None
    normalization: NormalizationSpec | None = None
    source: str | None = None


def _validate_url(value: str | None) -> str | None:
    if value is None:
        return value
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("URL must use http or https")
    return value


class ModelRecord(StrictModel):
    schema_version: Literal["1.0"]
    model_id: Identifier
    model_name: NonEmptyStr
    year: int | None
    publication_type: PublicationType
    venue: NonEmptyStr
    model_category: NonEmptyStr
    modalities: Annotated[list[Modality], Field(min_length=1)]
    architecture: NonEmptyStr
    architecture_details: ArchitectureDetails | None = None
    pretraining_data_summary: NonEmptyStr
    pretraining_strategy: NonEmptyStr
    reported_summary: NonEmptyStr
    paper_url: str | None
    code_url: str | None
    code_available: bool
    capabilities: list[Capability]
    benchmark_tracks: list[str]
    runtime_phase: RuntimePhase
    license: str | None
    license_verified: bool
    verification_status: VerificationStatus
    verification: VerificationBreakdown | None = None
    implementation: ImplementationStatus
    reported_tasks_text: NonEmptyStr
    provenance: Provenance
    notes: list[str]

    _paper_url = field_validator("paper_url")(_validate_url)
    _code_url = field_validator("code_url")(_validate_url)


class CheckpointRecord(StrictModel):
    schema_version: Literal["1.0"]
    checkpoint_id: CheckpointIdentifier
    model_id: Identifier
    checkpoint_name: NonEmptyStr
    artifact_type: ArtifactType | None = None
    modalities: Annotated[list[Modality], Field(min_length=1)]
    weight_url: str | None
    provider: Provider
    access_type: AccessType
    requires_auth: bool
    redistribution_allowed: Literal["yes", "no", "unknown"]
    license: str | None
    framework: str | None
    input_size: str | None
    input: InputSpec | None = None
    normalization: str | None
    preprocessing: PreprocessingSpec | None = None
    embedding_dim: int | None
    sha256: str | None
    source_commit: str | None
    verification_status: VerificationStatus
    verification: VerificationBreakdown | None = None
    last_verified: str | None
    provenance: Provenance
    notes: list[str]

    _weight_url = field_validator("weight_url")(_validate_url)
