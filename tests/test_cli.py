import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from typer.testing import CliRunner

from ophbench.cli import app
from ophbench.extraction.profiles import (
    load_extraction_defaults,
    resolve_extraction_profile,
)

ROOT = Path(__file__).parents[1]
runner = CliRunner()


def test_registry_and_catalog_cli_commands():
    assert runner.invoke(app, ["registry", "validate"]).exit_code == 0
    assert runner.invoke(app, ["catalog", "build", "--check"]).exit_code == 0


def test_model_inspection_cli_commands():
    list_result = runner.invoke(app, ["list-models"])
    show_result = runner.invoke(app, ["show-model", "retfound"])
    doctor_result = runner.invoke(app, ["doctor", "--model", "retfound"])
    assert list_result.exit_code == 0 and "retfound" in list_result.stdout
    assert show_result.exit_code == 0 and '"model_id": "retfound"' in show_result.stdout
    assert doctor_result.exit_code == 0 and '"checkpoint_count": 2' in doctor_result.stdout


def test_doctor_script_forwards_command_line_arguments():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/doctor.py"), "--model", "retfound"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert '"model_id": "retfound"' in result.stdout


def test_import_script_forwards_command_line_arguments(tmp_path: Path):
    source = ROOT / "seed/ophthalmic_models_seed_v0.xlsx"
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/import_seed_xlsx.py"), "--input", str(source)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert len(list((tmp_path / "registry/models").glob("*.yaml"))) == 15


def test_short_extract_profile_resolves_registry_and_local_checkpoint(tmp_path: Path):
    checkpoint = tmp_path / "retfound.pth"
    checkpoint.write_bytes(b"weights")
    config = tmp_path / "config.yaml"
    config.write_text(
        f"checkpoints:\n  retfound-cfp: {checkpoint.as_posix()}\n",
        encoding="utf-8",
    )
    values, loaded_path = load_extraction_defaults(config)
    resolved = resolve_extraction_profile(
        profile="retfound-cfp",
        model_id=None,
        checkpoint_id=None,
        checkpoint_path=None,
        values=values,
        config_path=loaded_path,
    )
    assert resolved.model_id == "retfound"
    assert resolved.checkpoint_id == "retfound-cfp"
    assert resolved.checkpoint_path == checkpoint.resolve()


def test_short_extract_cli_preserves_legacy_options(monkeypatch, tmp_path: Path):
    checkpoint = tmp_path / "retfound.pth"
    checkpoint.write_bytes(b"weights")
    config = tmp_path / "config.yaml"
    config.write_text(
        f"checkpoints:\n  retfound-cfp: {checkpoint.as_posix()}\n",
        encoding="utf-8",
    )
    captured = {}

    def fake_run_extraction(extraction_config):
        captured["config"] = extraction_config
        return SimpleNamespace(success_count=8, failure_count=0, embedding_dim=1024)

    monkeypatch.setattr("ophbench.cli.run_extraction", fake_run_extraction)
    result = runner.invoke(
        app,
        [
            "extract",
            "retfound-cfp",
            "--input",
            str(tmp_path / "images"),
            "--output",
            str(tmp_path / "features"),
            "--config",
            str(config),
        ],
    )
    assert result.exit_code == 0
    assert "8 success" in result.stdout
    assert captured["config"].model_id == "retfound"
    assert captured["config"].checkpoint_id == "retfound-cfp"
