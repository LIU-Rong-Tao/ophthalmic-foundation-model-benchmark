import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

SCRIPT = Path("scripts/download_checkpoint_asset.py")
SPEC = importlib.util.spec_from_file_location("download_checkpoint_asset", SCRIPT)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def test_huggingface_url_uses_registered_repo_and_filename():
    plan = {
        "provider": "huggingface",
        "registered_weight_url": "https://huggingface.co/example/model",
        "actual_filename": "weights/model.safetensors",
    }
    assert module.source_url(plan, {}) == (
        "https://huggingface.co/example/model/resolve/main/weights/model.safetensors"
    )


def test_non_ready_checkpoint_is_blocked(tmp_path: Path):
    plan = {
        "download_status": "authentication_required",
        "actual_filename": "model.pth",
        "model_id": "demo",
        "checkpoint_id": "demo-default",
    }
    try:
        module.download_one(
            plan=plan,
            access={},
            checkpoint=SimpleNamespace(sha256=None),
            cache_root=tmp_path,
            manifest_path=tmp_path / "manifest.csv",
            token=None,
        )
    except ValueError as exc:
        assert "ready_to_download" in str(exc)
    else:
        raise AssertionError("authentication-required checkpoint must not download")
