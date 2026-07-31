"""Official visual-only adapters for RET-CLIP and ViLReF.

Both projects vendor the OpenAI CLIP ViT implementation and expose
``encode_image`` as the image feature API.  The adapters below reproduce only
that official visual branch, load it strictly from the local checkpoints, and
use each repository's deterministic evaluation transform.  Text encoders are
intentionally not constructed.
"""

from __future__ import annotations

from pathlib import Path

from ..base import ImageEncoderAdapter
from ..errors import AdapterEnvironmentError, CheckpointResolutionError, InvalidCheckpointError
from .eyeclip import EyeCLIPAdapter, _visual_model_type


class _OfficialClipVisualAdapter(ImageEncoderAdapter):
    input_size = 224
    embedding_dim = 512
    adapter_version = "0.3.0"
    capabilities = ("image_encoding", "feature_extraction")
    normalization = {
        "mean": (0.48145466, 0.4578275, 0.40821073),
        "std": (0.26862954, 0.26130258, 0.27577711),
    }
    state_dict_field: str | None = None
    state_prefix = "module.visual."
    official_source = ""

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

    def _checkpoint_state(self, container):
        if self.state_dict_field is None:
            state = container
        elif isinstance(container, dict):
            state = container.get(self.state_dict_field)
        else:
            state = None
        if not isinstance(state, dict):
            raise InvalidCheckpointError(
                f"Expected checkpoint state_dict field {self.state_dict_field!r}"
            )
        return state

    def load(self):
        available, message = self.check_environment()
        if not available:
            raise AdapterEnvironmentError(message)
        import torch

        container = torch.load(
            self.resolve_checkpoint(),
            map_location="cpu",
            weights_only=True,
        )
        source = self._checkpoint_state(container)
        visual = {
            key.removeprefix(self.state_prefix): value
            for key, value in source.items()
            if key.startswith(self.state_prefix)
        }
        config = EyeCLIPAdapter._derive_visual_config(visual)
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
        strict_match = not missing and not unexpected and not shape_mismatches
        audit = {
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
            "visual_config": config,
            "feature_node": "official encode_image: CLS after ln_post and visual.proj",
            "official_source": self.official_source,
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
        self.load_audit = audit
        self.visual_config = config
        return self

    def preprocess(self, image):
        try:
            from torchvision import transforms
        except ImportError as exc:
            raise AdapterEnvironmentError(
                f"{self.model_id} preprocessing requires torchvision"
            ) from exc
        return transforms.Compose(
            [
                transforms.Lambda(lambda value: value.convert("RGB")),
                transforms.Resize(
                    (self.input_size, self.input_size),
                    interpolation=transforms.InterpolationMode.BICUBIC,
                ),
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
                f"Unexpected {self.model_id} embedding shape: {tuple(embedding.shape)}"
            )
        return embedding

    def runtime_metadata(self) -> dict:
        return {
            "feature_node": "official encode_image: CLS after ln_post and visual.proj",
            "embedding_dim": self.embedding_dim,
            "preprocessing_id": self.preprocessing_id,
            "official_source": self.official_source,
            "visual_config": self.visual_config,
            "load_audit": self.load_audit,
        }


class RETCLIPAdapter(_OfficialClipVisualAdapter):
    """RET-CLIP official ViT-B/16 visual encoder."""

    model_id = "ret-clip"
    checkpoint_id = "ret-clip-default"
    preprocessing_id = "ret-clip-official-224-square-bicubic-clip-normalize"
    official_source = "RET_CLIP/clip/model.py::encode_image + RET_CLIP/clip/utils.py"


class ViLReFAdapter(_OfficialClipVisualAdapter):
    """ViLReF official ViT-B/16 visual encoder."""

    model_id = "vilref"
    checkpoint_id = "vilref-default"
    preprocessing_id = "vilref-official-224-square-bicubic-clip-normalize"
    state_dict_field = "state_dict"
    official_source = "ViLReF/clip/model.py::encode_image + ViLReF/clip/utils.py"
