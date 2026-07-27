import csv
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from ophbench.extraction import ExtractionConfig, ExtractionError, run_extraction


class FakeAdapter:
    adapter_version = "test"
    preprocessing_id = "test-rgb"

    def __init__(self, **kwargs):
        self.model = None

    def load(self):
        return self

    def preprocess(self, image):
        import torch

        return torch.tensor([float(np.asarray(image).mean())], dtype=torch.float32)

    def encode_image(self, batch):
        import torch

        return torch.cat([batch, batch + 1], dim=1)


def fake_factory(**kwargs):
    return FakeAdapter(**kwargs)


def _config(tmp_path: Path, image_dir: Path, **changes):
    values = dict(
        model_id="fake",
        checkpoint_id="fake-v1",
        checkpoint=tmp_path / "weights.bin",
        output_dir=tmp_path / "output",
        input_dir=image_dir,
        batch_size=2,
        shard_size=2,
    )
    values.update(changes)
    return ExtractionConfig(**values)


def test_directory_extraction_is_sharded_and_isolates_decode_failure(tmp_path):
    images = tmp_path / "images"
    images.mkdir()
    for name, color in (("a.png", 10), ("b.jpg", 20), ("c.tiff", 30)):
        Image.new("RGB", (8, 8), color=(color, color, color)).save(images / name)
    (images / "broken.png").write_bytes(b"not an image")
    (tmp_path / "weights.bin").write_bytes(b"fake weights")

    result = run_extraction(_config(tmp_path, images), adapter_factory=fake_factory)

    assert result.success_count == 3 and result.failure_count == 1 and result.embedding_dim == 2
    with (result.output_dir / "samples.csv").open(encoding="utf-8") as handle:
        samples = list(csv.DictReader(handle))
    assert [row["sample_id"] for row in samples] == ["a.png", "b.jpg", "c.tiff"]
    assert len(list((result.output_dir / "features").glob("*.npy"))) == 2
    assert (result.output_dir / "artifact_manifest.json").is_file()


def test_manifest_input_and_resume_fingerprint_guard(tmp_path):
    images = tmp_path / "images"
    images.mkdir()
    Image.new("RGB", (8, 8), color=(2, 2, 2)).save(images / "one.png")
    (tmp_path / "weights.bin").write_bytes(b"fake weights")
    manifest = tmp_path / "manifest.csv"
    manifest.write_text("sample_id,image_path\nx1,images/one.png\n", encoding="utf-8")
    config = _config(tmp_path, images, input_dir=None, manifest=manifest)
    assert run_extraction(config, adapter_factory=fake_factory).success_count == 1
    assert run_extraction(config, adapter_factory=fake_factory).completed is True
    with pytest.raises(ExtractionError, match="fingerprint"):
        run_extraction(_config(tmp_path, images, checkpoint_id="other", resume=True), adapter_factory=fake_factory)


def test_interrupted_run_resumes_after_a_completed_shard(tmp_path):
    images = tmp_path / "images"
    images.mkdir()
    for index in range(3):
        Image.new("RGB", (8, 8), color=(index, index, index)).save(images / f"{index}.png")
    (tmp_path / "weights.bin").write_bytes(b"fake weights")

    class InterruptingAdapter(FakeAdapter):
        calls = 0

        def encode_image(self, batch):
            self.__class__.calls += 1
            if self.__class__.calls == 2:
                raise KeyboardInterrupt("test interruption")
            return super().encode_image(batch)

    config = _config(tmp_path, images, batch_size=1, shard_size=1)
    with pytest.raises(KeyboardInterrupt):
        run_extraction(config, adapter_factory=lambda **_: InterruptingAdapter())
    resumed = run_extraction(
        _config(tmp_path, images, batch_size=1, shard_size=1, resume=True), adapter_factory=fake_factory
    )
    assert resumed.success_count == 3
