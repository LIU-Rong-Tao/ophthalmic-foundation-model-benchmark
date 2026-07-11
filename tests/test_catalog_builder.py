from pathlib import Path

from ophbench.registry.builder import build_catalog


def test_catalog_build_is_stable_and_check_detects_stale(tmp_path: Path):
    source = Path("registry")
    build_catalog(source, tmp_path)
    first = {p.name: p.read_bytes() for p in tmp_path.iterdir() if p.is_file()}
    build_catalog(source, tmp_path, check=True)
    build_catalog(source, tmp_path)
    second = {p.name: p.read_bytes() for p in tmp_path.iterdir() if p.is_file()}
    assert first == second
    (tmp_path / "models.json").write_text("stale", encoding="utf-8")
    assert build_catalog(source, tmp_path, check=True).is_stale


def test_catalog_outputs_expected_files(tmp_path: Path):
    result = build_catalog(Path("registry"), tmp_path)
    assert result.model_count == 15
    assert result.checkpoint_count == 27
    assert {"models.csv", "checkpoints.csv", "models.json", "checkpoints.json", "MODEL_ZOO.md"} <= {
        p.name for p in tmp_path.iterdir()
    }
