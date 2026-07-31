from pathlib import Path

import pytest

from ophbench import load_adapter
from ophbench.models.adapters.clip_family import RETCLIPAdapter, ViLReFAdapter
from ophbench.models.adapters.flair_family import (
    FLAIRAdapter,
    KeepFITFLAIRAdapter,
    KeepFITHalfFLAIRAdapter,
)
from ophbench.models.adapters.retizero import RetiZeroAdapter
from ophbench.models.adapters.urfound import UrFoundAdapter
from ophbench.models.errors import CheckpointResolutionError


@pytest.mark.parametrize(
    ("model_id", "checkpoint_id", "adapter_type", "embedding_dim"),
    [
        ("flair", "flair-default", FLAIRAdapter, 2048),
        ("keepfit", "keepfit-flair-mmretinal-cfp", KeepFITFLAIRAdapter, 2048),
        (
            "keepfit",
            "keepfit-half-flair-mmretinal-cfp",
            KeepFITHalfFLAIRAdapter,
            2048,
        ),
        ("ret-clip", "ret-clip-default", RETCLIPAdapter, 512),
        ("vilref", "vilref-default", ViLReFAdapter, 512),
        ("retizero", "retizero-default", RetiZeroAdapter, 1024),
        ("urfound", "urfound-default", UrFoundAdapter, 768),
    ],
)
def test_public_factory_dispatches_verified_adapters(
    tmp_path: Path,
    model_id: str,
    checkpoint_id: str,
    adapter_type: type,
    embedding_dim: int,
):
    adapter = load_adapter(
        model_id=model_id,
        checkpoint_id=checkpoint_id,
        checkpoint_path=tmp_path / "weights",
    )
    assert isinstance(adapter, adapter_type)
    assert adapter.embedding_dim == embedding_dim


@pytest.mark.parametrize(
    "adapter",
    [
        FLAIRAdapter(),
        KeepFITFLAIRAdapter(),
        KeepFITHalfFLAIRAdapter(),
        RETCLIPAdapter(),
        ViLReFAdapter(),
        RetiZeroAdapter(),
        UrFoundAdapter(),
    ],
)
def test_verified_adapters_require_explicit_local_checkpoint(adapter):
    with pytest.raises(CheckpointResolutionError, match="explicit local checkpoint_path"):
        adapter.resolve_checkpoint()


@pytest.mark.parametrize(
    ("adapter", "expected_shape"),
    [
        (FLAIRAdapter(Path("unused")), (3, 512, 512)),
        (KeepFITFLAIRAdapter(Path("unused")), (3, 512, 512)),
        (RETCLIPAdapter(Path("unused")), (3, 224, 224)),
        (ViLReFAdapter(Path("unused")), (3, 224, 224)),
        (RetiZeroAdapter(Path("unused")), (3, 224, 224)),
        (UrFoundAdapter(Path("unused")), (3, 224, 224)),
    ],
)
def test_verified_adapter_preprocessing_is_deterministic(adapter, expected_shape):
    torch = pytest.importorskip("torch")
    pytest.importorskip("torchvision")
    image_module = pytest.importorskip("PIL.Image")
    image = image_module.new("RGB", (321, 279), color=(127, 64, 32))
    first = adapter.preprocess(image)
    second = adapter.preprocess(image)
    assert first.shape == expected_shape
    assert first.dtype == torch.float32
    assert torch.isfinite(first).all()
    assert torch.equal(first, second)
