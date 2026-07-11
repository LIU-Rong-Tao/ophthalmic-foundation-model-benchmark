from pathlib import Path

import pytest

from ophbench import load_adapter
from ophbench.models.adapters.retfound_cfp import EnvironmentCheck, RETFoundCFPAdapter
from ophbench.models.errors import CheckpointResolutionError, InvalidCheckpointError


def test_public_factory_dispatches_retfound_cfp(tmp_path):
    adapter = load_adapter(
        model_id="retfound",
        checkpoint_id="retfound-cfp",
        checkpoint_path=tmp_path / "weights.pth",
    )
    assert isinstance(adapter, RETFoundCFPAdapter)
    assert adapter.embedding_dim == 1024


def test_missing_checkpoint_is_explicit():
    adapter = RETFoundCFPAdapter()
    with pytest.raises(CheckpointResolutionError, match="explicit checkpoint_path"):
        adapter.resolve_checkpoint()


def test_invalid_checkpoint_format_is_rejected(tmp_path):
    torch = pytest.importorskip("torch")
    path = tmp_path / "invalid.pth"
    torch.save({"unexpected": {}}, path)
    adapter = RETFoundCFPAdapter(path)
    adapter.check_environment = lambda: EnvironmentCheck(True, (), "available")
    monkey_model = object()
    adapter._model_type = lambda: monkey_model
    with pytest.raises(InvalidCheckpointError, match="'model' state dict"):
        adapter.load()


def test_preprocess_matches_official_eval_shape():
    torch = pytest.importorskip("torch")
    pytest.importorskip("torchvision")
    image_module = pytest.importorskip("PIL.Image")
    adapter = RETFoundCFPAdapter(Path("unused"))
    tensor = adapter.preprocess(image_module.new("L", (320, 280), color=127))
    assert tensor.shape == (3, 256, 256)
    assert tensor.dtype == torch.float32
    assert torch.isfinite(tensor).all()
