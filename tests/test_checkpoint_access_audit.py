import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

SCRIPT = Path("scripts/audit_checkpoint_access.py")
SPEC = importlib.util.spec_from_file_location("checkpoint_access_audit", SCRIPT)
assert SPEC and SPEC.loader
audit = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = audit
SPEC.loader.exec_module(audit)


def test_google_drive_file_id_parses_supported_urls():
    assert audit.google_drive_file_id("https://drive.google.com/file/d/abc-123/view") == "abc-123"
    assert audit.google_drive_file_id("https://drive.google.com/open?id=xyz") == "xyz"
    assert audit.google_drive_file_id(None) is None


def test_missing_url_is_not_silently_skipped():
    checkpoint = SimpleNamespace(
        model_id="demo",
        checkpoint_id="demo-default",
        checkpoint_name="Default",
        weight_url=None,
        provider="unknown",
        requires_auth=False,
        verification=None,
    )
    row = audit.audit_checkpoint(checkpoint, session=None, hf_token=None)
    assert row.access_status == "official_file_missing"
    assert row.server_accessible is False


def test_download_plan_requires_verified_server_access(tmp_path: Path):
    row = audit.AuditRow(
        model_id="demo",
        checkpoint_id="demo-default",
        checkpoint_name="Default",
        declared_url="https://example.test/file.bin",
        resolved_url="https://example.test/file.bin",
        provider="other",
        official_source_status="source_unverified",
        access_status="verified_accessible",
        authentication_required=False,
        server_accessible=True,
        actual_filename="file.bin",
        size_bytes=123,
        content_type="application/octet-stream",
        probe_result="ok",
        failure_reason=None,
        checked_at="2026-01-01T00:00:00Z",
    )
    plan = audit.build_download_plan([row], cache_root=tmp_path)
    assert plan[0]["downloadable_now"] is True
    assert plan[0]["recommended_local_path"].endswith("demo/demo-default/file.bin")


def test_huggingface_file_probe_reports_authentication_requirement(monkeypatch):
    import huggingface_hub

    checkpoint = SimpleNamespace(
        model_id="demo",
        checkpoint_id="demo-default",
        checkpoint_name="Default",
        weight_url="https://huggingface.co/example/demo",
        provider="huggingface",
        requires_auth=False,
        verification=None,
    )
    monkeypatch.setattr(
        huggingface_hub.HfApi,
        "repo_info",
        lambda *_args, **_kwargs: SimpleNamespace(
            siblings=[SimpleNamespace(rfilename="weights/model.pth", size=123)]
        ),
    )

    def fake_probe(url, *, session, headers=None):
        assert url.endswith("weights/model.pth")
        assert headers == {"Authorization": "Bearer test-token"}
        return {
            "status": 401,
            "url": url,
            "headers": {"content-type": "application/json"},
            "sample": b'{"error":"unauthorized"}',
        }

    monkeypatch.setattr(audit, "_request_probe", fake_probe)
    row = audit.audit_checkpoint(checkpoint, session=object(), hf_token="test-token")

    assert row.access_status == "authentication_required"
    assert row.authentication_required is True
    assert row.server_accessible is False
    assert row.size_bytes == 123
