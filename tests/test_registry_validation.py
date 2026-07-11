from copy import deepcopy

import pytest

from ophbench.registry.schemas import CheckpointRecord, ModelRecord
from ophbench.registry.validator import RegistryValidationError, validate_records


def model_data(model_id="sample"):
    return {
        "schema_version": "1.0",
        "model_id": model_id,
        "model_name": "Sample",
        "year": 2024,
        "publication_type": "journal",
        "venue": "Journal",
        "model_category": "visual",
        "modalities": ["CFP"],
        "architecture": "ViT",
        "pretraining_data_summary": "data",
        "pretraining_strategy": "MAE",
        "reported_summary": "Reported by source.",
        "paper_url": "https://example.org/paper",
        "code_url": "https://example.org/code",
        "code_available": True,
        "capabilities": ["image_encoding"],
        "benchmark_tracks": [],
        "runtime_phase": "phase1_image_encoder",
        "license": None,
        "license_verified": False,
        "verification_status": "seed_unverified",
        "implementation": {
            "adapter_status": "not_started",
            "smoke_test_status": "not_run",
            "benchmark_status": "not_run",
        },
        "reported_tasks_text": "classification",
        "provenance": {
            "source_file": "seed.xlsx",
            "source_sheet": "Sheet1",
            "source_row": 2,
            "imported_at": "2026-07-11T00:00:00Z",
        },
        "notes": [],
    }


def checkpoint_data(checkpoint_id="sample-default", model_id="sample"):
    return {
        "schema_version": "1.0",
        "checkpoint_id": checkpoint_id,
        "model_id": model_id,
        "checkpoint_name": "Default",
        "modalities": ["CFP"],
        "weight_url": "https://example.org/w",
        "provider": "other",
        "access_type": "unknown",
        "requires_auth": False,
        "redistribution_allowed": "unknown",
        "license": None,
        "framework": None,
        "input_size": None,
        "normalization": None,
        "embedding_dim": None,
        "sha256": None,
        "source_commit": None,
        "verification_status": "seed_unverified",
        "last_verified": None,
        "provenance": {
            "source_file": "seed.xlsx",
            "source_sheet": "Sheet1",
            "source_row": 2,
            "imported_at": "2026-07-11T00:00:00Z",
        },
        "notes": [],
    }


def test_duplicate_model_id_fails():
    model = ModelRecord.model_validate(model_data())
    with pytest.raises(RegistryValidationError, match="Duplicate model_id"):
        validate_records([model, model], [])


def test_duplicate_checkpoint_id_fails():
    model = ModelRecord.model_validate(model_data())
    cp = CheckpointRecord.model_validate(checkpoint_data())
    with pytest.raises(RegistryValidationError, match="Duplicate checkpoint_id"):
        validate_records([model], [cp, cp])


def test_missing_model_reference_fails():
    with pytest.raises(RegistryValidationError, match="unknown model_id"):
        validate_records([], [CheckpointRecord.model_validate(checkpoint_data())])


@pytest.mark.parametrize("field,value", [("paper_url", "ftp://bad"), ("publication_type", "book")])
def test_invalid_model_field_fails(field, value):
    data = deepcopy(model_data())
    data[field] = value
    with pytest.raises(ValueError):
        ModelRecord.model_validate(data)


def test_missing_required_field_fails():
    data = model_data()
    del data["model_name"]
    with pytest.raises(ValueError):
        ModelRecord.model_validate(data)


@pytest.mark.parametrize("field", ["model_id", "model_name", "architecture"])
def test_required_model_strings_cannot_be_empty(field):
    data = model_data()
    data[field] = ""
    with pytest.raises(ValueError):
        ModelRecord.model_validate(data)


@pytest.mark.parametrize("model_id", ["RET Found", "ret_found", "retfound!", "-retfound"])
def test_model_id_must_be_kebab_case(model_id):
    data = model_data(model_id=model_id)
    with pytest.raises(ValueError):
        ModelRecord.model_validate(data)


def test_checkpoint_id_must_be_kebab_case():
    data = checkpoint_data(checkpoint_id="Bad Checkpoint")
    with pytest.raises(ValueError):
        CheckpointRecord.model_validate(data)


def test_unknown_modality_fails_schema_validation():
    data = model_data()
    data["modalities"] = ["fundus_photo"]
    with pytest.raises(ValueError):
        ModelRecord.model_validate(data)


def test_unknown_capability_fails_schema_validation():
    data = model_data()
    data["capabilities"] = ["anything"]
    with pytest.raises(ValueError):
        ModelRecord.model_validate(data)
