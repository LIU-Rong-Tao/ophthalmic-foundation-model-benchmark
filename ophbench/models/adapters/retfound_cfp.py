from __future__ import annotations

import argparse
import hashlib
from dataclasses import asdict, dataclass
from functools import partial
from pathlib import Path
from typing import Any

from ..base import ImageEncoderAdapter
from ..errors import AdapterEnvironmentError, CheckpointResolutionError, InvalidCheckpointError


@dataclass(frozen=True)
class EnvironmentCheck:
    available: bool
    missing: tuple[str, ...]
    message: str


class RETFoundCFPAdapter(ImageEncoderAdapter):
    """RETFound MAE ViT-L/16 CFP image encoder using the official eval protocol."""

    model_id = "retfound"
    checkpoint_id = "retfound-cfp"
    capabilities = ("image_encoding", "feature_extraction")
    adapter_version = "0.2.0"
    input_size = 256
    embedding_dim = 1024
    normalization = {
        "mean": (0.485, 0.456, 0.406),
        "std": (0.229, 0.224, 0.225),
    }

    def __init__(self, checkpoint_path=None, device="cpu"):
        self.checkpoint_path = Path(checkpoint_path).expanduser() if checkpoint_path else None
        self.device = str(device)
        self.model = None

    def check_environment(self) -> EnvironmentCheck:
        missing = []
        for module in ("torch", "torchvision", "timm", "PIL"):
            try:
                __import__(module)
            except ImportError:
                missing.append(module)
        return EnvironmentCheck(
            not missing,
            tuple(missing),
            (
                "RETFound runtime is available"
                if not missing
                else f"Missing optional dependencies: {', '.join(missing)}"
            ),
        )

    def resolve_checkpoint(self) -> Path:
        if self.checkpoint_path is None:
            raise CheckpointResolutionError(
                "RETFound CFP requires an explicit checkpoint_path; authenticated weights "
                "are never downloaded automatically."
            )
        path = self.checkpoint_path.resolve()
        if not path.is_file():
            raise CheckpointResolutionError(f"RETFound CFP checkpoint does not exist: {path}")
        return path

    @staticmethod
    def _model_type():
        import torch
        import torch.nn as nn
        from timm.models.vision_transformer import VisionTransformer

        class OfficialRETFoundVisionTransformer(VisionTransformer):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.fc_norm = kwargs["norm_layer"](kwargs["embed_dim"])
                del self.norm

            def forward_features(self, x):
                x = self.patch_embed(x)
                cls_tokens = self.cls_token.expand(x.shape[0], -1, -1)
                x = torch.cat((cls_tokens, x), dim=1)
                x = self.pos_drop(x + self.pos_embed)
                for block in self.blocks:
                    x = block(x)
                return self.fc_norm(x[:, 1:, :].mean(dim=1))

        return OfficialRETFoundVisionTransformer(
            img_size=256,
            patch_size=16,
            embed_dim=1024,
            depth=24,
            num_heads=16,
            mlp_ratio=4,
            qkv_bias=True,
            norm_layer=partial(nn.LayerNorm, eps=1e-6),
            num_classes=0,
        )

    def load(self):
        check = self.check_environment()
        if not check.available:
            raise AdapterEnvironmentError(check.message)
        import torch

        path = self.resolve_checkpoint()
        with torch.serialization.safe_globals([argparse.Namespace]):
            checkpoint = torch.load(path, map_location="cpu", weights_only=True)
        if not isinstance(checkpoint, dict) or not isinstance(checkpoint.get("model"), dict):
            raise InvalidCheckpointError(
                "Expected an official RETFound checkpoint containing a 'model' state dict"
            )
        state = dict(checkpoint["model"])
        if "patch_embed.proj.weight" not in state or "pos_embed" not in state:
            raise InvalidCheckpointError("RETFound checkpoint is missing ViT encoder tensors")
        model = self._model_type()
        for key in ("head.weight", "head.bias"):
            state.pop(key, None)
        self._interpolate_position_embedding(model, state)
        encoder_state = {key: value for key, value in state.items() if key in model.state_dict()}
        model.load_state_dict(encoder_state, strict=False)
        self.model = model.to(self.device).eval()
        return self

    @staticmethod
    def _interpolate_position_embedding(model, state):
        import torch

        position = state["pos_embed"]
        num_patches = model.patch_embed.num_patches
        extra_tokens = model.pos_embed.shape[-2] - num_patches
        old_size = int((position.shape[-2] - extra_tokens) ** 0.5)
        new_size = int(num_patches**0.5)
        if old_size == new_size:
            return
        prefix = position[:, :extra_tokens]
        patches = position[:, extra_tokens:]
        patches = patches.reshape(-1, old_size, old_size, position.shape[-1]).permute(0, 3, 1, 2)
        patches = torch.nn.functional.interpolate(
            patches, size=(new_size, new_size), mode="bicubic", align_corners=False
        )
        patches = patches.permute(0, 2, 3, 1).flatten(1, 2)
        state["pos_embed"] = torch.cat((prefix, patches), dim=1)

    def preprocess(self, image: Any):
        try:
            from torchvision import transforms
        except ImportError as exc:
            raise AdapterEnvironmentError(
                "RETFound preprocessing requires the optional torchvision dependency"
            ) from exc

        transform = transforms.Compose(
            [
                transforms.Resize(
                    self.input_size, interpolation=transforms.InterpolationMode.BICUBIC
                ),
                transforms.CenterCrop(self.input_size),
                transforms.ToTensor(),
                transforms.Normalize(**self.normalization),
            ]
        )
        if getattr(image, "mode", None) != "RGB":
            image = image.convert("RGB")
        return transform(image)

    def encode_image(self, image):
        if self.model is None:
            raise RuntimeError("Call load() before encode_image()")
        import torch

        tensor = self.preprocess(image) if not torch.is_tensor(image) else image
        if tensor.ndim == 3:
            tensor = tensor.unsqueeze(0)
        with torch.inference_mode():
            embedding = self.model.forward_features(tensor.to(self.device))
        if embedding.ndim != 2 or embedding.shape[-1] != self.embedding_dim:
            raise RuntimeError(f"Unexpected RETFound embedding shape: {tuple(embedding.shape)}")
        return embedding

    def smoke_manifest(self) -> dict[str, Any]:
        path = self.resolve_checkpoint()
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        check = self.check_environment()
        return {
            "model_id": self.model_id,
            "checkpoint_id": self.checkpoint_id,
            "checkpoint_path": str(path),
            "checkpoint_size": path.stat().st_size,
            "checkpoint_sha256": digest.hexdigest(),
            "device": self.device,
            "adapter_version": self.adapter_version,
            "input_size": self.input_size,
            "embedding_dim": self.embedding_dim,
            "environment": asdict(check),
        }
