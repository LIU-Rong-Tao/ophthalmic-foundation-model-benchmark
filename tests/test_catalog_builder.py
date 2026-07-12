from pathlib import Path

from ophbench.registry.builder import build_catalog
from ophbench.registry.loader import load_registry


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
    cards = sorted((tmp_path / "model_cards").glob("*.md"))
    assert len(cards) == 15


def test_model_zoo_links_and_checkpoint_cards_are_complete(tmp_path: Path):
    build_catalog(Path("registry"), tmp_path)
    models, checkpoints = load_registry(Path("registry"))
    zoo = (tmp_path / "MODEL_ZOO.md").read_text(encoding="utf-8")
    for model in models:
        assert f"model_cards/{model.model_id}.md" in zoo
        card = tmp_path / "model_cards" / f"{model.model_id}.md"
        assert card.is_file()
        content = card.read_text(encoding="utf-8")
        for checkpoint in [item for item in checkpoints if item.model_id == model.model_id]:
            assert f"`{checkpoint.checkpoint_id}`" in content


def test_unverified_model_card_does_not_claim_verified_evidence(tmp_path: Path):
    build_catalog(Path("registry"), tmp_path)
    content = (tmp_path / "model_cards" / "deretfound.md").read_text(encoding="utf-8")
    assert "## 待核验事项" in content
    assert "| 许可证 | 待核验 |" in content


def test_retfound_card_exposes_checkpoint_level_evidence(tmp_path: Path):
    build_catalog(Path("registry"), tmp_path)
    content = (tmp_path / "model_cards" / "retfound.md").read_text(encoding="utf-8")
    assert "ViT-Large/16 / masked_autoencoding" in content
    assert "`retfound-cfp` / CFP" in content
    assert "`retfound-oct` / OCT" in content
    assert "embedding 维度 1024" in content
    assert "| Checkpoint 文件 | 待核验 |" in content
