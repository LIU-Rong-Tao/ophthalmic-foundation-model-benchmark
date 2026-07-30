"""EyeCLIP official visual encoder adapter.

The module implements the CLIP-style visual branch and preprocessing defined in
EyeCLIP's official ``eyeclip/model.py`` and ``eyeclip/clip.py``.  Text and MAE
decoder weights are intentionally excluded from frozen image embeddings.
"""

from __future__ import annotations

from collections import OrderedDict
from pathlib import Path

from ..base import ImageEncoderAdapter
from ..errors import AdapterEnvironmentError, CheckpointResolutionError, InvalidCheckpointError


class _LayerNorm:
    @staticmethod
    def type():
        import torch.nn as nn

        class LayerNorm(nn.LayerNorm):
            def forward(self, value):
                return super().forward(value.float()).to(value.dtype)

        return LayerNorm


def _visual_model_type(config: dict[str, int]):
    import torch
    import torch.nn as nn

    LayerNorm = _LayerNorm.type()

    class QuickGELU(nn.Module):
        def forward(self, value):
            return value * torch.sigmoid(1.702 * value)

    class ResidualAttentionBlock(nn.Module):
        def __init__(self, width: int, heads: int):
            super().__init__()
            self.attn = nn.MultiheadAttention(width, heads)
            self.ln_1 = LayerNorm(width)
            self.mlp = nn.Sequential(
                OrderedDict(
                    [
                        ("c_fc", nn.Linear(width, width * 4)),
                        ("gelu", QuickGELU()),
                        ("c_proj", nn.Linear(width * 4, width)),
                    ]
                )
            )
            self.ln_2 = LayerNorm(width)

        def forward(self, value):
            normalized = self.ln_1(value)
            value = value + self.attn(
                normalized,
                normalized,
                normalized,
                need_weights=False,
            )[0]
            return value + self.mlp(self.ln_2(value))

    class Transformer(nn.Module):
        def __init__(self, width: int, layers: int, heads: int):
            super().__init__()
            self.resblocks = nn.Sequential(
                *[ResidualAttentionBlock(width, heads) for _ in range(layers)]
            )

        def forward(self, value):
            return self.resblocks(value)

    class EyeCLIPVision(nn.Module):
        def __init__(self):
            super().__init__()
            width = config["width"]
            patch_size = config["patch_size"]
            resolution = config["input_size"]
            self.conv1 = nn.Conv2d(
                3,
                width,
                kernel_size=patch_size,
                stride=patch_size,
                bias=False,
            )
            self.class_embedding = nn.Parameter(torch.empty(width))
            self.positional_embedding = nn.Parameter(
                torch.empty((resolution // patch_size) ** 2 + 1, width)
            )
            self.ln_pre = LayerNorm(width)
            self.transformer = Transformer(width, config["layers"], config["heads"])
            self.ln_post = LayerNorm(width)
            self.proj = nn.Parameter(torch.empty(width, config["output_dim"]))

        def forward(self, image):
            value = self.conv1(image)
            value = value.reshape(value.shape[0], value.shape[1], -1).permute(0, 2, 1)
            cls = self.class_embedding.to(value.dtype) + torch.zeros(
                value.shape[0],
                1,
                value.shape[-1],
                dtype=value.dtype,
                device=value.device,
            )
            value = torch.cat([cls, value], dim=1)
            value = value + self.positional_embedding.to(value.dtype)
            value = self.ln_pre(value).permute(1, 0, 2)
            value = self.transformer(value).permute(1, 0, 2)
            return self.ln_post(value[:, 0, :]) @ self.proj

    return EyeCLIPVision()


class EyeCLIPAdapter(ImageEncoderAdapter):
    """Strict local EyeCLIP visual encoder for 512-dimensional image features."""

    model_id = "eyeclip"
    checkpoint_id = "eyeclip-default"
    capabilities = ("image_encoding", "feature_extraction")
    adapter_version = "0.3.0"
    preprocessing_id = "eyeclip-official-224-bicubic-center-crop-clip-normalize"
    input_size = 224
    embedding_dim = 512
    normalization = {
        "mean": (0.48145466, 0.4578275, 0.40821073),
        "std": (0.26862954, 0.26130258, 0.27577711),
    }

    def __init__(self, checkpoint_path=None, device="cpu"):
        self.checkpoint_path = (
            Path(checkpoint_path).expanduser() if checkpoint_path else None
        )
        self.device = str(device)
        self.model = None
        self.load_audit: dict | None = None
        self.visual_config: dict[str, int] | None = None

    def check_environment(self):
        missing = []
        for module in ("torch", "torchvision", "PIL"):
            try:
                __import__(module)
            except ImportError:
                missing.append(module)
        return (
            not missing,
            (
                "EyeCLIP visual runtime is available"
                if not missing
                else f"Missing optional dependencies: {', '.join(missing)}"
            ),
        )

    def resolve_checkpoint(self) -> Path:
        if self.checkpoint_path is None:
            raise CheckpointResolutionError(
                "EyeCLIP requires an explicit local checkpoint_path; weights are never "
                "downloaded automatically."
            )
        path = self.checkpoint_path.resolve()
        if not path.is_file():
            raise CheckpointResolutionError(f"EyeCLIP checkpoint does not exist: {path}")
        return path

    @staticmethod
    def _derive_visual_config(state) -> dict[str, int]:
        import math

        required = ("conv1.weight", "positional_embedding", "proj")
        missing = [key for key in required if key not in state]
        if missing:
            raise InvalidCheckpointError(
                f"EyeCLIP visual checkpoint is missing tensors: {missing}"
            )
        width = int(state["conv1.weight"].shape[0])
        patch_size = int(state["conv1.weight"].shape[-1])
        grid_size = round(math.sqrt(int(state["positional_embedding"].shape[0]) - 1))
        layers = len(
            {
                key.split(".")[2]
                for key in state
                if key.startswith("transformer.resblocks.") and len(key.split(".")) > 3
            }
        )
        config = {
            "width": width,
            "layers": layers,
            "heads": width // 64,
            "patch_size": patch_size,
            "input_size": grid_size * patch_size,
            "output_dim": int(state["proj"].shape[1]),
        }
        if config["input_size"] != 224 or config["output_dim"] != 512:
            raise InvalidCheckpointError(
                "The local EyeCLIP checkpoint is not the verified 224px/512d visual model: "
                f"{config}"
            )
        return config

    def load(self):
        available, message = self.check_environment()
        if not available:
            raise AdapterEnvironmentError(message)
        import torch

        path = self.resolve_checkpoint()
        container = torch.load(path, map_location="cpu", weights_only=True)
        if not isinstance(container, dict) or not isinstance(
            container.get("model_state_dict"),
            dict,
        ):
            raise InvalidCheckpointError(
                "Expected an official EyeCLIP checkpoint containing model_state_dict"
            )
        source = container["model_state_dict"]
        visual = {
            key.removeprefix("visual."): value
            for key, value in source.items()
            if key.startswith("visual.") and not key.startswith("visual.decoder.")
        }
        config = self._derive_visual_config(visual)
        model = _visual_model_type(config)
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
        audit = {
            "checkpoint_total_keys": len(source),
            "checkpoint_visual_keys": sum(key.startswith("visual.") for key in source),
            "checkpoint_visual_decoder_keys_excluded": sum(
                key.startswith("visual.decoder.") for key in source
            ),
            "current_visual_model_keys": len(target),
            "successfully_loaded_visual_keys": len(matched),
            "missing_visual_keys": missing,
            "unexpected_visual_keys": unexpected,
            "shape_mismatches": shape_mismatches,
            "visual_key_coverage": len(matched) / len(target),
            "visual_parameter_coverage": loaded_parameters / total_parameters,
            "visual_strict_match": not missing
            and not unexpected
            and not shape_mismatches,
            "visual_config": config,
            "feature_node": "visual CLS token after ln_post and visual.proj",
            "text_encoder_participates": False,
            "mae_decoder_participates": False,
            "classification_head_participates": False,
        }
        if not audit["visual_strict_match"]:
            raise InvalidCheckpointError(
                "EyeCLIP visual strict-load gate failed: "
                f"missing={missing}, unexpected={unexpected}, "
                f"shape_mismatches={shape_mismatches}"
            )
        model.load_state_dict(visual, strict=True)
        self.model = model.to(self.device).eval()
        self.load_audit = audit
        self.visual_config = config
        return self

    def preprocess(self, image):
        try:
            from torchvision import transforms
        except ImportError as exc:
            raise AdapterEnvironmentError(
                "EyeCLIP preprocessing requires the optional torchvision dependency"
            ) from exc

        transform = transforms.Compose(
            [
                transforms.Resize(
                    self.input_size,
                    interpolation=transforms.InterpolationMode.BICUBIC,
                ),
                transforms.CenterCrop(self.input_size),
                transforms.Lambda(lambda value: value.convert("RGB")),
                transforms.ToTensor(),
                transforms.Normalize(**self.normalization),
            ]
        )
        return transform(image)

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
            raise RuntimeError(f"Unexpected EyeCLIP embedding shape: {tuple(embedding.shape)}")
        return embedding

    def runtime_metadata(self) -> dict:
        return {
            "feature_node": "visual CLS token after ln_post and visual.proj",
            "embedding_dim": self.embedding_dim,
            "preprocessing_id": self.preprocessing_id,
            "visual_config": self.visual_config,
            "load_audit": self.load_audit,
        }
