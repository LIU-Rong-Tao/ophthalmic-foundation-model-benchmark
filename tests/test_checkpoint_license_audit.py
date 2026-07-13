import importlib.util
import sys
from pathlib import Path

SCRIPT = Path("scripts/audit_checkpoint_license.py")
SPEC = importlib.util.spec_from_file_location("checkpoint_license_audit", SCRIPT)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def test_code_and_weight_license_are_distinguished():
    status, code, weight, reason = module.classify_license(
        code_evidence={"reachable": True},
        registered_status="repository_license_present_weight_scope_unverified",
        weight_reachable=True,
    )
    assert status == "license_review_required"
    assert code == "declared_code_license_page_reachable"
    assert weight == "weight_scope_unverified"
    assert reason


def test_explicit_weight_license_can_be_verified():
    status, code, weight, _ = module.classify_license(
        code_evidence={"reachable": True},
        registered_status="apache-2.0_code_and_weights_declared",
        weight_reachable=True,
    )
    assert status == "license_verified"
    assert code.startswith("declared_")
    assert weight == "explicit_weight_terms_declared"


def test_unreachable_license_stays_review_required():
    status, _, _, _ = module.classify_license(
        code_evidence={"reachable": False},
        registered_status="not_declared",
        weight_reachable=True,
    )
    assert status == "license_review_required"
