from pathlib import Path

from ophbench.registry.importer import EXPECTED_CHECKPOINT_IDS, MODEL_ID_MAP, import_seed


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
