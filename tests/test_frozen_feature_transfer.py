import json
from pathlib import Path

import numpy as np
import torch
import yaml
from PIL import Image

from ophbench.evaluation.frozen_feature import (
    OUTPUT_FILES,
    compare_reproduction_runs,
    load_protocol,
    run_frozen_feature_transfer,
)

CLASSES = ("anodr", "bmilddr", "cmoderatedr", "dseveredr", "eproliferativedr")


class FakeAdapter:
    adapter_version = "test"

    def load(self):
        return self

    def preprocess(self, image):
        value = float(np.asarray(image).mean() / 255.0)
        return torch.tensor([value], dtype=torch.float32)

    def encode_image(self, batch):
        value = batch[:, :1]
        return torch.cat([value, value**2, value**3, torch.ones_like(value)], dim=1)


def fake_factory(**kwargs):
    return FakeAdapter()


def _dataset(root: Path):
    for split_index, split in enumerate(("train", "val", "test")):
        for label, class_name in enumerate(CLASSES):
            directory = root / split / class_name
            directory.mkdir(parents=True, exist_ok=True)
            for sample in range(3):
                value = 20 + label * 45 + sample
                Image.new("RGB", (12, 12), color=(value, value, value)).save(
                    directory / f"{split}_{split_index}_{label}_{sample}.png"
                )


def _protocol(tmp_path: Path) -> Path:
    source = Path(__file__).resolve().parents[1] / "protocols/frozen_feature_transfer_v0_1.yaml"
    payload = yaml.safe_load(source.read_text(encoding="utf-8"))
    payload["evaluation"]["bootstrap"]["resamples"] = 20
    path = tmp_path / "protocol.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def test_protocol_is_clean_and_contains_no_neural_training_fields():
    root = Path(__file__).resolve().parents[1]
    protocol = load_protocol(root / "protocols/frozen_feature_transfer_v0_1.yaml")
    serialized = json.dumps(protocol)
    for forbidden in ("optimizer", "scheduler", "learning_rate", "augmentation"):
        assert forbidden not in serialized


def test_pilot_outputs_are_complete_and_reproducible(tmp_path):
    data_root = tmp_path / "APTOS2019"
    _dataset(data_root)
    checkpoint = tmp_path / "checkpoint.pth"
    checkpoint.write_bytes(b"fixture")
    protocol = _protocol(tmp_path)
    runs = []
    for name in ("run-1", "run-2"):
        runs.append(
            run_frozen_feature_transfer(
                protocol,
                data_root=data_root,
                checkpoint_path=checkpoint,
                output_dir=tmp_path / name,
                device="cpu",
                batch_size=8,
                adapter_factory=fake_factory,
            )
        )
    for run in runs:
        assert OUTPUT_FILES.issubset({path.name for path in run.iterdir()})
        assert (run / "artifact_manifest.json").is_file()
        manifest = json.loads((run / "run_manifest.json").read_text())
        assert manifest["evaluation_role"] == "pilot_protocol_validation"
        assert manifest["research_claim_status"] == "not_for_scientific_comparison"
        assert manifest["label_space"] == "dr_icdr_0_4"
        assert manifest["patient_level_claim_allowed"] is False
    assert compare_reproduction_runs(*runs)["reproducible"] is True
