from __future__ import annotations

from pathlib import Path

from ..base import ImageEncoderAdapter
from ..errors import AdapterEnvironmentError, CheckpointResolutionError, InvalidCheckpointError


class RETFoundGreenAdapter(ImageEncoderAdapter):
    """RETFound-Green v0.1: official DINOv2 ViT-S/14 + four register tokens."""

    model_id = "retfound-green"
    checkpoint_id = "retfound-green-v0.1"
    capabilities = ("image_encoding", "feature_extraction")
    adapter_version = "0.3.0"
    preprocessing_id = "retfound-green-official-392-rgb-half"
    input_size = 392
    embedding_dim = 384
    normalization = {"mean": (0.5, 0.5, 0.5), "std": (0.5, 0.5, 0.5)}

    def __init__(self, checkpoint_path=None, device="cpu"):
        self.checkpoint_path = Path(checkpoint_path).expanduser() if checkpoint_path else None
        self.device = str(device)
        self.model = None

    def check_environment(self):
        try:
            import timm  # noqa: F401
            import torch  # noqa: F401
            import torchvision  # noqa: F401
        except ImportError as exc:
            return False, str(exc)
        return True, "RETFound-Green runtime is available"

    def load(self):
        available, message = self.check_environment()
        if not available:
            raise AdapterEnvironmentError(message)
        if self.checkpoint_path is None or not self.checkpoint_path.is_file():
            raise CheckpointResolutionError("RETFound-Green requires an explicit local checkpoint_path")
        import torch
        import timm

        checkpoint = torch.load(self.checkpoint_path, map_location="cpu", weights_only=True)
        state = checkpoint.get("state_dict", checkpoint.get("model", checkpoint)) if isinstance(checkpoint, dict) else None
        if not isinstance(state, dict):
            raise InvalidCheckpointError("RETFound-Green checkpoint does not contain a state dict")
        state = {key.removeprefix("module."): value for key, value in state.items()}
        model = timm.create_model("vit_small_patch14_reg4_dinov2", img_size=(392, 392), num_classes=0)
        mismatch = model.load_state_dict(state, strict=False)
        required = {"cls_token", "pos_embed", "patch_embed.proj.weight", "norm.weight"}
        missing_required = required & set(mismatch.missing_keys)
        if missing_required:
            raise InvalidCheckpointError(f"RETFound-Green encoder parameters missing: {sorted(missing_required)}")
        self.model = model.to(self.device).eval()
        return self

    def preprocess(self, image):
        from torchvision import transforms

        if image.mode != "RGB":
            image = image.convert("RGB")
        return transforms.Compose([
            transforms.Resize((self.input_size, self.input_size), interpolation=transforms.InterpolationMode.BICUBIC),
            transforms.ToTensor(),
            transforms.Normalize(**self.normalization),
        ])(image)

    def encode_image(self, image):
        import torch

        if self.model is None:
            raise RuntimeError("Call load() before encode_image()")
        tensor = self.preprocess(image) if not torch.is_tensor(image) else image
        if tensor.ndim == 3:
            tensor = tensor.unsqueeze(0)
        with torch.inference_mode():
            features = self.model.forward_features(tensor.to(self.device))
            if features.ndim == 3:
                features = features[:, self.model.num_prefix_tokens :].mean(dim=1)
        if features.ndim != 2 or features.shape[-1] != self.embedding_dim:
            raise RuntimeError(f"Unexpected RETFound-Green embedding shape: {tuple(features.shape)}")
        return features
