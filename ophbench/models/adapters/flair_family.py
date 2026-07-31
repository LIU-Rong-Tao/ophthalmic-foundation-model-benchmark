"""Official frozen visual backbone adapters for FLAIR and KeepFIT CFP.

The official linear-probe entry points construct a ResNet-50 visual encoder,
replace its classifier with ``Identity``, and can disable the multimodal
projection head.  OphBench follows that official pre-classifier path and emits
the resulting 2048-dimensional frozen embedding.
"""

from __future__ import annotations

from pathlib import Path

from ..base import ImageEncoderAdapter
from ..errors import AdapterEnvironmentError, CheckpointResolutionError, InvalidCheckpointError


class _OfficialFlairBackboneAdapter(ImageEncoderAdapter):
    input_size = 512
    embedding_dim = 2048
    adapter_version = "0.3.0"
    capabilities = ("image_encoding", "feature_extraction")
    state_prefix = "vision_model.model."
    checkpoint_format = "torch"
    official_source = ""

    def __init__(self, checkpoint_path=None, device="cpu"):
        self.checkpoint_path = (
            Path(checkpoint_path).expanduser() if checkpoint_path else None
        )
        self.device = str(device)
        self.model = None
        self.load_audit: dict | None = None

    def check_environment(self):
        missing = []
        for module in ("torch", "torchvision", "PIL"):
            try:
                __import__(module)
            except ImportError:
                missing.append(module)
        if self.checkpoint_format == "safetensors":
            try:
                __import__("safetensors")
            except ImportError:
                missing.append("safetensors")
        return (
            not missing,
            (
                f"{self.model_id} official visual runtime is available"
                if not missing
                else f"Missing optional dependencies: {', '.join(missing)}"
            ),
        )

    def resolve_checkpoint(self) -> Path:
        if self.checkpoint_path is None:
            raise CheckpointResolutionError(
                f"{self.model_id} requires an explicit local checkpoint_path"
            )
        path = self.checkpoint_path.resolve()
        if not path.is_file():
            raise CheckpointResolutionError(f"Checkpoint does not exist: {path}")
        return path

    def _state_dict(self, path: Path):
        if self.checkpoint_format == "safetensors":
            from safetensors.torch import load_file

            return load_file(str(path), device="cpu")
        import torch

        state = torch.load(path, map_location="cpu", weights_only=True)
        if not isinstance(state, dict):
            raise InvalidCheckpointError("Expected a state-dict checkpoint")
        return state

    def load(self):
        available, message = self.check_environment()
        if not available:
            raise AdapterEnvironmentError(message)
        import torchvision

        source = self._state_dict(self.resolve_checkpoint())
        visual = {
            key.removeprefix(self.state_prefix): value
            for key, value in source.items()
            if key.startswith(self.state_prefix)
        }
        model = torchvision.models.resnet50(weights=None)
        import torch.nn as nn

        model.fc = nn.Identity()
        target = model.state_dict()
        missing = [key for key in target if key not in visual]
        unexpected = [key for key in visual if key not in target]
        shape_mismatches = [
            {
                "key": key,
                "checkpoint_shape": list(visual[key].shape),
                "model_shape": list(target[key].shape),
            }
            for key in target
            if key in visual and tuple(visual[key].shape) != tuple(target[key].shape)
        ]
        matched = [
            key
            for key in target
            if key in visual and tuple(visual[key].shape) == tuple(target[key].shape)
        ]
        total_parameters = sum(value.numel() for value in target.values())
        loaded_parameters = sum(target[key].numel() for key in matched)
        strict_match = not missing and not unexpected and not shape_mismatches
        self.load_audit = {
            "checkpoint_total_keys": len(source),
            "checkpoint_visual_backbone_keys": len(visual),
            "current_visual_backbone_keys": len(target),
            "successfully_loaded_visual_keys": len(matched),
            "missing_visual_keys": missing,
            "unexpected_visual_keys": unexpected,
            "shape_mismatches": shape_mismatches,
            "visual_key_coverage": len(matched) / len(target),
            "visual_parameter_coverage": loaded_parameters / total_parameters,
            "visual_strict_match": strict_match,
            "feature_node": "official linear-probe path: ResNet-50 before projection/classifier",
            "official_source": self.official_source,
            "projection_head_participates": False,
            "text_encoder_participates": False,
            "classification_head_participates": False,
        }
        if not strict_match:
            raise InvalidCheckpointError(
                f"{self.model_id} visual strict-load gate failed: "
                f"missing={missing}, unexpected={unexpected}, "
                f"shape_mismatches={shape_mismatches}"
            )
        model.load_state_dict(visual, strict=True)
        self.model = model.to(self.device).eval().requires_grad_(False)
        return self

    def preprocess(self, image):
        try:
            import torch
            from torchvision.transforms import InterpolationMode
            from torchvision.transforms import functional as functional
        except ImportError as exc:
            raise AdapterEnvironmentError(
                f"{self.model_id} preprocessing requires torch and torchvision"
            ) from exc
        value = functional.pil_to_tensor(image.convert("RGB")).to(torch.float32) / 255.0
        height, width = value.shape[-2:]
        scale = max(height, width) / self.input_size
        resized_height = max(1, int(height / scale))
        resized_width = max(1, int(width / scale))
        value = functional.resize(
            value,
            [resized_height, resized_width],
            interpolation=InterpolationMode.BILINEAR,
            antialias=True,
        )
        return functional.pad(
            value,
            [0, 0, self.input_size - resized_width, self.input_size - resized_height],
            fill=0,
        )

    def encode_image(self, image):
        if self.model is None:
            raise RuntimeError("Call load() before encode_image()")
        import torch

        tensor = self.preprocess(image) if not torch.is_tensor(image) else image
        if tensor.ndim == 3:
            tensor = tensor.unsqueeze(0)
        with torch.inference_mode():
            embedding = self.model(tensor.to(self.device))
        if embedding.ndim != 2 or embedding.shape[-1] != self.embedding_dim:
            raise RuntimeError(
                f"Unexpected {self.model_id} embedding shape: {tuple(embedding.shape)}"
            )
        return embedding

    def runtime_metadata(self) -> dict:
        return {
            "feature_node": "official linear-probe path: ResNet-50 before projection/classifier",
            "embedding_dim": self.embedding_dim,
            "preprocessing_id": self.preprocessing_id,
            "official_source": self.official_source,
            "load_audit": self.load_audit,
        }


class FLAIRAdapter(_OfficialFlairBackboneAdapter):
    """FLAIR official ResNet-50 pre-projection visual backbone."""

    model_id = "flair"
    checkpoint_id = "flair-default"
    checkpoint_format = "safetensors"
    preprocessing_id = "flair-official-512-aspect-pad-zero-to-one"
    official_source = "flair/modeling/model.py::VisionModel + preprocess_image"


class KeepFITFLAIRAdapter(_OfficialFlairBackboneAdapter):
    """KeepFIT CFP official ResNet-50 pre-projection visual backbone."""

    model_id = "keepfit"
    checkpoint_id = "keepfit-flair-mmretinal-cfp"
    preprocessing_id = "keepfit-cfp-official-512-aspect-pad-zero-to-one"
    official_source = (
        "KeepFIT/KeepFIT-CFP/keepfit/modeling/model.py::VisionModel + preprocess_image"
    )


class KeepFITHalfFLAIRAdapter(KeepFITFLAIRAdapter):
    """KeepFIT 50%-FLAIR CFP checkpoint on the same official visual runtime."""

    checkpoint_id = "keepfit-half-flair-mmretinal-cfp"
