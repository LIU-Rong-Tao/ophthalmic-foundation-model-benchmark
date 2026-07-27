from pathlib import Path
import re

import ophbench
from ophbench import get_registry_info, list_checkpoints, list_models, load_registry

ROOT = Path(__file__).resolve().parents[1]


def test_public_api_loads_packaged_registry_without_source_path(monkeypatch, tmp_path: Path):
    monkeypatch.chdir(tmp_path)
    snapshot = load_registry()

    assert snapshot.model_count == 15
    assert snapshot.checkpoint_count == 27
    assert snapshot.package_version == "0.3.0"
    assert snapshot.schema_version == "1.0"
    assert snapshot.registry_source == "package:ophbench/_registry_data"


def test_public_api_lists_models_and_retfound_checkpoints():
    models = list_models()
    checkpoints = list_checkpoints("retfound")

    assert len(models) == 15
    assert [checkpoint.checkpoint_id for checkpoint in checkpoints] == [
        "retfound-cfp",
        "retfound-oct",
    ]


def test_public_api_supports_explicit_development_registry_root():
    snapshot = load_registry(Path("registry"))
    info = get_registry_info(Path("registry"))

    assert snapshot.model_count == info.model_count == 15
    assert snapshot.checkpoint_count == info.checkpoint_count == 27
    assert snapshot.registry_source.endswith("registry")


def test_public_exports_are_explicit():
    assert ophbench.__version__ == "0.3.0"
    assert set(ophbench.__all__) == {
        "RegistrySnapshot",
        "__version__",
        "get_registry_info",
        "list_checkpoints",
        "list_models",
        "load_adapter",
        "load_registry",
    }


def test_package_version_has_one_consistent_value():
    pyproject_text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    declared = re.search(r'^version = "([^"]+)"$', pyproject_text, re.MULTILINE).group(1)
    snapshot = ophbench.load_registry(ROOT / "registry")
    assert declared == ophbench.__version__ == snapshot.package_version


def test_packaged_registry_copy_matches_authoritative_yaml():
    root = Path("registry")
    packaged = Path("ophbench/_registry_data")
    authoritative_files = {
        path.relative_to(root): path.read_bytes()
        for path in root.rglob("*.yaml")
    }
    packaged_files = {
        path.relative_to(packaged): path.read_bytes()
        for path in packaged.rglob("*.yaml")
    }
    assert packaged_files == authoritative_files
