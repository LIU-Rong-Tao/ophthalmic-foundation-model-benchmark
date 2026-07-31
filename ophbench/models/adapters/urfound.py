"""UrFound official CFP encoder adapter.

The adapter follows ``finetune/models_vit.py::forward_features`` and
``finetune/datasets_finetune.py::build_transform`` from the official UrFound
repository.  Only the ViT-B/16 encoder is loaded; reconstruction and language
decoders in the pretraining checkpoint are excluded.
"""

from __future__ import annotations

import argparse
from functools import partial
from pathlib import Path

from ..base import ImageEncoderAdapter
from ..errors import AdapterEnvironmentError, CheckpointResolutionError, InvalidCheckpointError


def _build_urfound_encoder():
    import torch
    import torch.nn as nn
    from timm.models.vision_transformer import VisionTransformer

    class UrFoundEncoder(VisionTransformer):
        def __init__(self):
            super().__init__(
                img_size=224,
                patch_size=16,
                in_chans=3,
                num_classes=0,
                embed_dim=768,
                depth=12,
                num_heads=12,
                mlp_ratio=4,
                qkv_bias=True,
                norm_layer=partial(nn.LayerNorm, eps=1e-6),
            )

        def forward(self, image):
            value = self.patch_embed(image)
            cls_tokens = self.cls_token.expand(value.shape[0], -1, -1)
            value = torch.cat((cls_tokens, value), dim=1)
            value = self.pos_drop(value + self.pos_embed)
            for block in self.blocks:
                value = block(value)
            return self.norm(value)[:, 0]

    return UrFoundEncoder()


class UrFoundAdapter(ImageEncoderAdapter):
    """Strict UrFound ViT-B/16 encoder for 768-dimensional CFP features."""

    model_id = "urfound"
    checkpoint_id = "urfound-default"
    capabilities = ("image_encoding", "feature_extraction")
    adapter_version = "0.3.0"
    preprocessing_id = "urfound-official-eval-256-center-crop-224-imagenet"
    input_size = 224
    embedding_dim = 768
    normalization = {
        "mean": (0.485, 0.456, 0.406),
        "std": (0.229, 0.224, 0.225),
    }

    def __init__(self, checkpoint_path=None, device="cpu"):
        self.checkpoint_path = (
            Path(checkpoint_path).expanduser() if checkpoint_path else None
        )
        self.device = str(device)
        self.model = None
        self.load_audit: dict | None = None

    def check_environment(self):
        missing = []
        for module in ("torch", "torchvision", "timm", "PIL"):
            try:
                __import__(module)
            except ImportError:
                missing.append(module)
        return (
            not missing,
            (
                "UrFound official encoder runtime is available"
                if not missing
                else f"Missing optional dependencies: {', '.join(missing)}"
            ),
        )

    def resolve_checkpoint(self) -> Path:
        if self.checkpoint_path is None:
            raise CheckpointResolutionError(
                "UrFound requires an explicit local checkpoint_path"
            )
        path = self.checkpoint_path.resolve()
        if not path.is_file():
            raise CheckpointResolutionError(f"UrFound checkpoint does not exist: {path}")
        return path

    def load(self):
        available, message = self.check_environment()
        if not available:
            raise AdapterEnvironmentError(message)
        import torch

        with torch.serialization.safe_globals([argparse.Namespace]):
            container = torch.load(
                self.resolve_checkpoint(),
                map_location="cpu",
                weights_only=True,
            )
        if not isinstance(container, dict) or not isinstance(container.get("model"), dict):
            raise InvalidCheckpointError(
                "Expected an official UrFound checkpoint containing model"
            )
        source = container["model"]
        model = _build_urfound_encoder()
        target = model.state_dict()
        encoder = {key: value for key, value in source.items() if key in target}
        missing = [key for key in target if key not in encoder]
        shape_mismatches = [
            {
                "key": key,
                "checkpoint_shape": list(encoder[key].shape),
                "model_shape": list(target[key].shape),
            }
            for key in target
            if key in encoder and tuple(encoder[key].shape) != tuple(target[key].shape)
        ]
        matched = [
            key
            for key in target
            if key in encoder and tuple(encoder[key].shape) == tuple(target[key].shape)
        ]
        encoder_prefixes = ("cls_token", "pos_embed", "patch_embed.", "blocks.", "norm.")
        unexpected_encoder = [
            key
            for key in source
            if key.startswith(encoder_prefixes) and key not in target
        ]
        total_parameters = sum(value.numel() for value in target.values())
        loaded_parameters = sum(target[key].numel() for key in matched)
        strict_match = not missing and not unexpected_encoder and not shape_mismatches
        self.load_audit = {
            "checkpoint_total_keys": len(source),
            "current_encoder_keys": len(target),
            "successfully_loaded_encoder_keys": len(matched),
            "missing_encoder_keys": missing,
            "unexpected_encoder_keys": unexpected_encoder,
            "shape_mismatches": shape_mismatches,
            "encoder_key_coverage": len(matched) / len(target),
            "encoder_parameter_coverage": loaded_parameters / total_parameters,
            "encoder_strict_match": strict_match,
            "feature_node": "official forward_features CLS token after encoder norm",
            "official_source": (
                "finetune/models_vit.py::forward_features + "
                "finetune/datasets_finetune.py::build_transform"
            ),
            "decoder_participates": False,
            "text_encoder_participates": False,
            "classification_head_participates": False,
        }
        if not strict_match:
            raise InvalidCheckpointError(
                "UrFound encoder strict-load gate failed: "
                f"missing={missing}, unexpected={unexpected_encoder}, "
                f"shape_mismatches={shape_mismatches}"
            )
        model.load_state_dict(encoder, strict=True)
        self.model = model.to(self.device).eval().requires_grad_(False)
        return self

    def preprocess(self, image):
        try:
            from torchvision import transforms
        except ImportError as exc:
            raise AdapterEnvironmentError(
                "UrFound preprocessing requires torchvision"
            ) from exc
        return transforms.Compose(
            [
                transforms.Resize(
                    256,
                    interpolation=transforms.InterpolationMode.BICUBIC,
                ),
                transforms.CenterCrop(self.input_size),
                transforms.Lambda(lambda value: value.convert("RGB")),
                transforms.ToTensor(),
                transforms.Normalize(**self.normalization),
            ]
        )(image)

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
                f"Unexpected UrFound embedding shape: {tuple(embedding.shape)}"
            )
        return embedding

    def runtime_metadata(self) -> dict:
        return {
            "feature_node": "official forward_features CLS token after encoder norm",
            "embedding_dim": self.embedding_dim,
            "preprocessing_id": self.preprocessing_id,
            "load_audit": self.load_audit,
        }
