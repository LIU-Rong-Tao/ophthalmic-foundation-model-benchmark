import importlib.util
import sys
from pathlib import Path

SCRIPTS = Path("scripts").resolve()
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location(
    "checkpoint_provenance_audit", SCRIPTS / "audit_checkpoint_provenance.py"
)
assert SPEC and SPEC.loader
audit = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = audit
SPEC.loader.exec_module(audit)


def decide(**overrides):
    values = {
        "repository_class": "official",
        "exact_reference": True,
        "registered_url": "https://example.test/weight.pth",
        "access_status": "accessible_source_unverified",
        "evidence_fetch_ok": True,
        "model_id": "demo",
    }
    values.update(overrides)
    return audit.classify_provenance(**values)


def test_official_repository_direct_weight_is_verified():
    assert decide() == ("official_source_verified", "high")


def test_official_repository_huggingface_reference_is_verified():
    text = 'model = from_pretrained("official/model")'
    assert audit.reference_matches("https://huggingface.co/official/model", text)


def test_author_source_with_incomplete_chain_is_not_official():
    assert decide(repository_class="author") == ("author_source_probable", "medium")


def test_third_party_mirror_stays_third_party():
    assert decide(repository_class="third_party") == ("third_party_mirror", "medium")


def test_similar_username_without_official_link_is_ambiguous():
    assert decide(repository_class="unknown", exact_reference=False) == (
        "source_ambiguous",
        "low",
    )


def test_huggingface_gated_source_keeps_authentication_status():
    assert decide(access_status="authentication_required") == (
        "authentication_required",
        "high",
    )


def test_github_api_rate_limit_does_not_downgrade_strong_readme_evidence():
    assert decide(access_status="probe_failed", model_id="retfound-green") == (
        "official_source_verified",
        "high",
    )


def test_github_rate_limit_diagnostic_records_reset_time():
    class Response:
        status_code = 403
        headers = {
            "x-ratelimit-remaining": "0",
            "x-ratelimit-reset": "1783908000",
        }

    class Session:
        def get(self, *_args, **_kwargs):
            return Response()

    detail = audit.github_rate_limit_diagnostic(
        "https://github.com/example/demo/releases/tag/v1", session=Session()
    )
    assert detail and "remaining=0" in detail and "reset_at=" in detail


def test_mirage_ssl_failure_is_inconclusive():
    assert decide(access_status="probe_failed", model_id="mirage") == (
        "probe_inconclusive",
        "medium",
    )


def test_google_drive_html_does_not_imply_file_verification():
    status, _ = decide(access_status="manual_review_required")
    assert status == "official_source_verified"
    assert audit.url_identity("https://drive.google.com/file/d/abc/view") == (
        "google_drive",
        "abc",
    )


def test_reachable_link_does_not_auto_upgrade_without_exact_evidence():
    assert decide(exact_reference=False) == ("source_ambiguous", "low")


def test_missing_registered_source_is_not_found():
    assert decide(registered_url=None, exact_reference=False) == ("source_not_found", "low")


def test_evidence_fetch_failure_is_inconclusive():
    assert decide(evidence_fetch_ok=False) == ("probe_inconclusive", "low")


def test_signed_resolved_url_drops_temporary_huggingface_query():
    url = (
        "https://us.aws.cdn.hf.co/xet-bridge-us/file?"
        "Policy=secret&Signature=secret&Key-Pair-Id=secret"
    )
    assert audit.sanitize_resolved_url(url) == "https://us.aws.cdn.hf.co/xet-bridge-us/file"


def test_evidence_index_and_outputs_are_complete_and_redacted(tmp_path: Path):
    row = audit.ProvenanceRow(
        model_id="demo",
        checkpoint_id="demo-default",
        registered_url="https://example.test/file?token=[REDACTED]",
        resolved_url=None,
        official_paper_url="https://example.test/paper",
        official_code_url="https://github.com/example/demo",
        official_project_url="https://github.com/example/demo",
        weight_evidence_url="https://raw.githubusercontent.com/example/demo/abc/README.md",
        evidence_source_type="official_code_repository_readme",
        repository_owner="example",
        checkpoint_provider_owner="example",
        exact_checkpoint_name="Default",
        exact_filename="model.pth",
        source_commit_or_release="abc",
        model_modality="CFP",
        checkpoint_modality="CFP",
        license_url=None,
        license_status="not_declared",
        evidence_summary="official README links exact weight",
        provenance_status="official_source_verified",
        confidence="high",
        manual_review_reason=None,
        link_reachable=True,
        file_verified=False,
        adapter_smoke_passed=False,
        checked_at="2026-07-13T00:00:00Z",
        access_diagnostic=None,
        previous_access_status="accessible_source_unverified",
    )
    evidence = [
        {
            "model_id": "demo",
            "checkpoint_id": "demo-default",
            "supporting_url": row.weight_evidence_url,
            "evidence_type": row.evidence_source_type,
            "fetched_at": row.checked_at,
            "page_title": "Demo",
            "evidence_summary": row.evidence_summary,
        }
    ]
    run_dir = tmp_path / "run"
    audit.write_outputs(
        run_dir=run_dir,
        rows=[row],
        evidence_index=evidence,
        access_path=tmp_path / "access.csv",
        evidence_path=tmp_path / "evidence.yaml",
        run_id="test",
    )
    expected = {
        "checkpoint_provenance.csv",
        "checkpoint_provenance.json",
        "manual_review.csv",
        "summary.json",
        "report.html",
        "run_config.yaml",
        "evidence_index.json",
    }
    assert {path.name for path in run_dir.iterdir()} == expected
    index = __import__("json").loads((run_dir / "evidence_index.json").read_text())
    assert index[0]["checkpoint_id"] == "demo-default"
    serialized = "\n".join(path.read_text() for path in run_dir.iterdir())
    assert "Bearer secret" not in serialized
    assert "token=secret" not in serialized
    assert b"\r\n" not in (run_dir / "checkpoint_provenance.csv").read_bytes()
    assert b"\r\n" not in (run_dir / "manual_review.csv").read_bytes()
