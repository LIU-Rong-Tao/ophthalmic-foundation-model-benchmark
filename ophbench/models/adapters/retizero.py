"""RetiZero official LoRA-RETFound visual encoder adapter."""

from __future__ import annotations

from functools import partial
from pathlib import Path

from ..base import ImageEncoderAdapter
from ..errors import AdapterEnvironmentError, CheckpointResolutionError, InvalidCheckpointError


def _build_retizero_encoder(rank: int):
    import torch
    import torch.nn as nn
    from timm.models.vision_transformer import VisionTransformer

    class LoRAQKV(nn.Module):
        def __init__(self, qkv):
            super().__init__()
            width = qkv.in_features
            self.qkv = qkv
            self.linear_a_q = nn.Linear(width, rank, bias=False)
            self.linear_b_q = nn.Linear(rank, width, bias=False)
            self.linear_a_v = nn.Linear(width, rank, bias=False)
            self.linear_b_v = nn.Linear(rank, width, bias=False)
            self.dim = width

        def forward(self, value):
            qkv = self.qkv(value)
            qkv[:, :, : self.dim] += self.linear_b_q(self.linear_a_q(value))
            qkv[:, :, -self.dim :] += self.linear_b_v(self.linear_a_v(value))
            return qkv

    class RetiZeroEncoder(VisionTransformer):
        def __init__(self):
            super().__init__(
                img_size=224,
                patch_size=16,
                in_chans=3,
                num_classes=0,
                embed_dim=1024,
                depth=24,
                num_heads=16,
                mlp_ratio=4,
                qkv_bias=True,
                norm_layer=partial(nn.LayerNorm, eps=1e-6),
            )
            for block in self.blocks:
                block.attn.qkv = LoRAQKV(block.attn.qkv)

        def forward(self, image):
            value = self.patch_embed(image)
            cls_tokens = self.cls_token.expand(value.shape[0], -1, -1)
            value = torch.cat((cls_tokens, value), dim=1)
            value = self.pos_drop(value + self.pos_embed)
            for block in self.blocks:
                value = block(value)
            return self.norm(value)[:, 0]

    return RetiZeroEncoder()


class RetiZeroAdapter(ImageEncoderAdapter):
    """Strict RetiZero LoRA-ViT-L/16 encoder for 1024-dimensional features."""

    model_id = "retizero"
    checkpoint_id = "retizero-default"
    capabilities = ("image_encoding", "feature_extraction")
    adapter_version = "0.3.0"
    preprocessing_id = "retizero-official-224-square-imagenet"
    input_size = 224
    embedding_dim = 1024
    lora_rank = 8
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
                "RetiZero official visual runtime is available"
                if not missing
                else f"Missing optional dependencies: {', '.join(missing)}"
            ),
        )

    def resolve_checkpoint(self) -> Path:
        if self.checkpoint_path is None:
            raise CheckpointResolutionError(
                "RetiZero requires an explicit local checkpoint_path"
            )
        path = self.checkpoint_path.resolve()
        if not path.is_file():
            raise CheckpointResolutionError(f"RetiZero checkpoint does not exist: {path}")
        return path

    def load(self):
        available, message = self.check_environment()
        if not available:
            raise AdapterEnvironmentError(message)
        import torch

        source = torch.load(
            self.resolve_checkpoint(),
            map_location="cpu",
            weights_only=True,
        )
        if not isinstance(source, dict):
            raise InvalidCheckpointError("Expected an official RetiZero state dict")
        prefix = "vision_model.model.lora_vit."
        visual = {
            key.removeprefix(prefix): value
            for key, value in source.items()
            if key.startswith(prefix)
        }
        rank_key = "blocks.0.attn.qkv.linear_a_q.weight"
        if rank_key not in visual:
            raise InvalidCheckpointError("RetiZero checkpoint is missing LoRA tensors")
        rank = int(visual[rank_key].shape[0])
        if rank != self.lora_rank:
            raise InvalidCheckpointError(
                f"Expected official RetiZero LoRA rank {self.lora_rank}, got {rank}"
            )
        model = _build_retizero_encoder(rank)
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
            "checkpoint_visual_keys": len(visual),
            "current_visual_model_keys": len(target),
            "successfully_loaded_visual_keys": len(matched),
            "missing_visual_keys": missing,
            "unexpected_visual_keys": unexpected,
            "shape_mismatches": shape_mismatches,
            "visual_key_coverage": len(matched) / len(target),
            "visual_parameter_coverage": loaded_parameters / total_parameters,
            "visual_strict_match": strict_match,
            "lora_rank": rank,
            "feature_node": "official Model_Finetuing img_encoder before classifier",
            "official_source": (
                "clip_modules/modeling/LoraRETFound.py + "
                "LORA/lora_image_encoder.py + modeling/model.py"
            ),
            "projection_head_participates": False,
            "text_encoder_participates": False,
            "classification_head_participates": False,
        }
        if not strict_match:
            raise InvalidCheckpointError(
                "RetiZero visual strict-load gate failed: "
                f"missing={missing}, unexpected={unexpected}, "
                f"shape_mismatches={shape_mismatches}"
            )
        model.load_state_dict(visual, strict=True)
        self.model = model.to(self.device).eval().requires_grad_(False)
        return self

    def preprocess(self, image):
        try:
            from torchvision import transforms
        except ImportError as exc:
            raise AdapterEnvironmentError(
                "RetiZero preprocessing requires torchvision"
            ) from exc
        return transforms.Compose(
            [
                transforms.Lambda(lambda value: value.convert("RGB")),
                transforms.Resize((self.input_size, self.input_size)),
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
                f"Unexpected RetiZero embedding shape: {tuple(embedding.shape)}"
            )
        return embedding

    def runtime_metadata(self) -> dict:
        return {
            "feature_node": "official Model_Finetuing img_encoder before classifier",
            "embedding_dim": self.embedding_dim,
            "preprocessing_id": self.preprocessing_id,
            "load_audit": self.load_audit,
        }
