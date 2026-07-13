import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

SCRIPT = Path("scripts/build_checkpoint_download_plan.py")
SPEC = importlib.util.spec_from_file_location("checkpoint_download_plan", SCRIPT)
assert SPEC and SPEC.loader
plan_module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = plan_module
SPEC.loader.exec_module(plan_module)


def test_authentication_blocks_download():
    status, reasons = plan_module.classify(
        access_status="authentication_required",
        provenance_status="authentication_required",
        license_status="apache-2.0_code_and_weights_declared",
        size_bytes=100,
        registered_url="https://example.test/model.pth",
    )
    assert status == "authentication_required"
    assert reasons


def test_license_scope_is_not_assumed():
    status, reasons = plan_module.classify(
        access_status="accessible_source_unverified",
        provenance_status="official_source_verified",
        license_status="research_and_education_only_noncommercial",
        size_bytes=100,
        registered_url="https://example.test/model.pth",
    )
    assert status == "license_review_required"
    assert reasons


def test_probe_failure_and_unknown_size_are_not_zero():
    status, reasons = plan_module.classify(
        access_status="probe_failed",
        provenance_status="official_source_verified",
        license_status="apache-2.0_code_and_weights_declared",
        size_bytes=None,
        registered_url="https://example.test/model.pth",
    )
    assert status == "probe_retry_required"
    assert "size_unknown" not in " ".join(reasons)


def test_build_plan_covers_registry_checkpoints(tmp_path: Path):
    cp = SimpleNamespace(
        checkpoint_id="demo-default",
        model_id="demo",
        checkpoint_name="Default",
        provider="other",
        weight_url="https://example.test/model.pth",
    )
    snapshot = SimpleNamespace(checkpoints=[cp])
    access = {
        "demo-default": {
            "checkpoint_id": "demo-default",
            "access_status": "accessible_source_unverified",
            "actual_filename": "model.pth",
            "size_bytes": "100",
            "failure_reason": "",
        }
    }
    provenance = {
        "demo-default": {
            "checkpoint_id": "demo-default",
            "provenance_status": "official_source_verified",
            "license_status": "apache-2.0_code_and_weights_declared",
            "exact_filename": "model.pth",
        }
    }
    plan, summary = plan_module.build_plan(
        access_rows=access,
        provenance_rows=provenance,
        snapshot=snapshot,
        cache_root=tmp_path,
    )
    assert plan[0]["download_status"] == "ready_to_download"
    assert plan[0]["size_status"] == "known"
    assert summary["ready_download_bytes"] == 100
