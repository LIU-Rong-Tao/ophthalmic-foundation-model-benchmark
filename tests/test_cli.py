import subprocess
import sys
from pathlib import Path

from typer.testing import CliRunner

from ophbench.cli import app

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
