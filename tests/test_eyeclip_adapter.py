from pathlib import Path

import pytest

from ophbench import load_adapter
from ophbench.models.adapters.eyeclip import EyeCLIPAdapter
from ophbench.models.errors import CheckpointResolutionError, InvalidCheckpointError


class _ShapeOnlyTensor:
    def __init__(self, *shape: int):
        self.shape = shape


def test_public_factory_dispatches_eyeclip(tmp_path: Path):
    adapter = load_adapter(
        model_id="eyeclip",
        checkpoint_id="eyeclip-default",
        checkpoint_path=tmp_path / "eyeclip.pt",
    )
    assert isinstance(adapter, EyeCLIPAdapter)
    assert adapter.embedding_dim == 512


def test_eyeclip_visual_config_is_derived_from_checkpoint_shapes():
    state = {
        "conv1.weight": _ShapeOnlyTensor(768, 3, 32, 32),
        "positional_embedding": _ShapeOnlyTensor(50, 768),
        "proj": _ShapeOnlyTensor(768, 512),
        **{
            f"transformer.resblocks.{index}.attn.in_proj_weight": _ShapeOnlyTensor(
                2304,
                768,
            )
            for index in range(12)
        },
    }
    assert EyeCLIPAdapter._derive_visual_config(state) == {
        "width": 768,
        "layers": 12,
        "heads": 12,
        "patch_size": 32,
        "input_size": 224,
        "output_dim": 512,
    }


def test_eyeclip_missing_checkpoint_is_explicit():
    with pytest.raises(CheckpointResolutionError, match="explicit local checkpoint_path"):
        EyeCLIPAdapter().resolve_checkpoint()


def test_eyeclip_invalid_checkpoint_container_is_rejected(tmp_path: Path):
    torch = pytest.importorskip("torch")
    path = tmp_path / "invalid.pt"
    torch.save({"unexpected": {}}, path)
    adapter = EyeCLIPAdapter(path)
    adapter.check_environment = lambda: (True, "available")
    with pytest.raises(InvalidCheckpointError, match="model_state_dict"):
        adapter.load()


def test_eyeclip_preprocess_matches_official_shape():
    torch = pytest.importorskip("torch")
    pytest.importorskip("torchvision")
    image_module = pytest.importorskip("PIL.Image")
    tensor = EyeCLIPAdapter(Path("unused")).preprocess(
        image_module.new("L", (320, 280), color=127)
    )
    assert tensor.shape == (3, 224, 224)
    assert tensor.dtype == torch.float32
    assert torch.isfinite(tensor).all()
