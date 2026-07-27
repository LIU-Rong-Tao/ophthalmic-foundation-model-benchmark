from __future__ import annotations

from pathlib import Path

from ..base import ImageEncoderAdapter
from ..errors import AdapterEnvironmentError, CheckpointResolutionError, InvalidCheckpointError


class EyeCLIPAdapter(ImageEncoderAdapter):
    """EyeCLIP's published ViT-B/32 visual encoder, without automatic CLIP downloads."""

    model_id = "eyeclip"
    checkpoint_id = "eyeclip-default"
    capabilities = ("image_encoding", "feature_extraction")
    adapter_version = "0.3.0"
    preprocessing_id = "eyeclip-clip-rgb-224-center-crop"
    input_size = 224
    embedding_dim = 512
    normalization = {"mean": (0.48145466, 0.4578275, 0.40821073), "std": (0.26862954, 0.26130258, 0.27577711)}

    def __init__(self, checkpoint_path=None, device="cpu"):
        self.checkpoint_path = Path(checkpoint_path).expanduser() if checkpoint_path else None
        self.device = str(device)
        self.model = None

    def load(self):
        if self.checkpoint_path is None or not self.checkpoint_path.is_file():
            raise CheckpointResolutionError("EyeCLIP requires an explicit local checkpoint_path")
        try:
            import clip.model
            import torch
        except ImportError as exc:
            raise AdapterEnvironmentError("EyeCLIP requires the official local OpenAI CLIP runtime") from exc
        checkpoint = torch.load(self.checkpoint_path, map_location="cpu", weights_only=True)
        state = checkpoint.get("state_dict", checkpoint.get("model", checkpoint)) if isinstance(checkpoint, dict) else None
        if not isinstance(state, dict):
            raise InvalidCheckpointError("EyeCLIP checkpoint does not contain a state dict")
        visual = {key.removeprefix("visual.").removeprefix("module.visual."): value for key, value in state.items() if key.startswith(("visual.", "module.visual."))}
        if not visual:
            visual = {key.removeprefix("module."): value for key, value in state.items()}
        model = clip.model.VisionTransformer(224, 32, 768, 12, 12, self.embedding_dim)
        mismatch = model.load_state_dict(visual, strict=False)
        required = {"conv1.weight", "class_embedding", "positional_embedding", "ln_post.weight", "proj"}
        missing = required & set(mismatch.missing_keys)
        if missing:
            raise InvalidCheckpointError(f"EyeCLIP visual encoder parameters missing: {sorted(missing)}")
        self.model = model.to(self.device).eval()
        return self

    def check_environment(self):
        try:
            import clip.model  # noqa: F401
            import torch  # noqa: F401
            import torchvision  # noqa: F401
        except ImportError as exc:
            return False, str(exc)
        return True, "EyeCLIP runtime is available"

    def preprocess(self, image):
        from torchvision import transforms

        if image.mode != "RGB":
            image = image.convert("RGB")
        return transforms.Compose([
            transforms.Resize(self.input_size, interpolation=transforms.InterpolationMode.BICUBIC),
            transforms.CenterCrop(self.input_size),
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
            features = self.model(tensor.to(self.device)).float()
        if features.ndim != 2 or features.shape[-1] != self.embedding_dim:
            raise RuntimeError(f"Unexpected EyeCLIP embedding shape: {tuple(features.shape)}")
        return features
