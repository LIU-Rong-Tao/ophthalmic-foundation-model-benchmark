from pathlib import Path

import yaml
from openpyxl import load_workbook

from ophbench.registry.importer import (
    EXPECTED_CHECKPOINT_IDS,
    MODEL_ID_MAP,
    _modalities,
    _parse_modalities,
    import_seed,
)


def test_oct_does_not_imply_ct_modality():
    assert _modalities("CFP、OCT") == ["CFP", "OCT"]
    assert _modalities("OCTA") == ["OCTA"]


def test_eyeclip_modalities_are_not_silently_dropped():
    text = "CFP、FFA、SLP、ICGA、OUS、OCT、SM、FAF、EEP、CT、RetCam + 报告"
    assert _modalities(text) == [
        "CFP",
        "OCT",
        "FFA",
        "ICGA",
        "FAF",
        "ultrasound",
        "external_eye",
        "slit_lamp",
        "specular_microscopy",
        "CT",
        "RetCam",
        "text",
    ]


def test_visionunite_modalities_include_pet_xray_and_fa():
    assert _modalities("CT、FA、CFP、MRI、OCT、PET、X-ray、文本") == [
        "CFP",
        "OCT",
        "FFA",
        "MRI",
        "CT",
        "PET",
        "X_ray",
        "text",
    ]


def test_unmapped_modality_token_is_reported():
    modalities, unmapped = _parse_modalities("CFP、XYZ")
    assert modalities == ["CFP", "other"]
    assert unmapped == ["XYZ"]


def test_import_writes_unmapped_modality_tokens_to_notes(tmp_path: Path):
    source = Path("seed/ophthalmic_models_seed_v0.xlsx")
    modified_source = tmp_path / "seed-with-unknown.xlsx"
    workbook = load_workbook(source)
    sheet = workbook["眼科大模型"]
    sheet["D2"] = f"{sheet['D2'].value}、XYZ"
    workbook.save(modified_source)
    import_seed(
        modified_source,
        tmp_path,
        imported_at="2026-07-11T00:00:00Z",
    )
    record = yaml.safe_load(
        (tmp_path / "registry/models/retfound.yaml").read_text(encoding="utf-8")
    )
    assert record["modalities"] == ["CFP", "OCT", "other"]
    assert "Unmapped modality tokens: XYZ" in record["notes"]


def test_seed_import_creates_expected_records(tmp_path: Path):
    result = import_seed(Path("seed/ophthalmic_models_seed_v0.xlsx"), tmp_path)
    model_ids = {path.stem for path in (tmp_path / "registry/models").glob("*.yaml")}
    checkpoint_ids = {path.stem for path in (tmp_path / "registry/checkpoints").glob("*.yaml")}
    assert result.model_count == 15
    assert result.checkpoint_count == 27
    assert model_ids == set(MODEL_ID_MAP.values())
    assert checkpoint_ids == set(EXPECTED_CHECKPOINT_IDS)


def test_seed_import_is_deterministic_except_manifest_timestamp(tmp_path: Path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    import_seed(
        Path("seed/ophthalmic_models_seed_v0.xlsx"), first, imported_at="2026-07-11T00:00:00Z"
    )
    import_seed(
        Path("seed/ophthalmic_models_seed_v0.xlsx"), second, imported_at="2026-07-11T00:00:00Z"
    )
    first_files = {p.relative_to(first): p.read_bytes() for p in first.rglob("*") if p.is_file()}
    second_files = {p.relative_to(second): p.read_bytes() for p in second.rglob("*") if p.is_file()}
    assert first_files == second_files
