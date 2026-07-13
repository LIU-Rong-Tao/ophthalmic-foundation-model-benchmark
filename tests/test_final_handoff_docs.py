from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "catalog" / "download_manifest.csv"
CATALOG = ROOT / "docs" / "MODEL_WEIGHT_CATALOG.md"
VERIFY = ROOT / "docs" / "DOWNLOAD_AND_VERIFY.md"
HANDOFF = ROOT / "docs" / "EVALUATION_HANDOFF.md"


def _rows() -> list[dict[str, str]]:
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_download_manifest_covers_registry_checkpoints() -> None:
    rows = _rows()
    assert len(rows) == 27
    assert len({row["checkpoint_id"] for row in rows}) == 27

    counts = Counter(row["status"] for row in rows)
    assert counts == {"downloaded_verified": 19, "excluded_by_project_scope": 8}

    downloaded = [row for row in rows if row["status"] == "downloaded_verified"]
    assert all(row["filename"] for row in downloaded)
    assert all(row["size_bytes"].isdigit() for row in downloaded)
    assert all(len(row["sha256"]) == 64 for row in downloaded)

    excluded = [row for row in rows if row["status"] == "excluded_by_project_scope"]
    assert {row["model_id"] for row in excluded} == {"visionfm"}
    assert all(row["download_enabled"] == "false" for row in excluded)
    expected_reason = (
        "Legacy/initial model of the current project; intentionally excluded "
        "from duplicate download."
    )
    assert all(row["skip_reason"] == expected_reason for row in excluded)


def test_retfound_assets_are_verified_but_future_access_is_gated() -> None:
    rows = {row["checkpoint_id"]: row for row in _rows()}
    for checkpoint_id in ("retfound-cfp", "retfound-oct"):
        row = rows[checkpoint_id]
        assert row["status"] == "downloaded_verified"
        assert row["sha256"]
        assert row["download_enabled"] == "false"
        assert "申请权限" in row["access_method"]


def test_human_catalog_contains_every_checkpoint() -> None:
    text = CATALOG.read_text(encoding="utf-8")
    for row in _rows():
        if row["model_id"] != "visionfm":
            assert row["checkpoint_id"] in text
    assert "影响因子" in text
    assert "SHA256" in text
    assert "使用限制 |" not in text
    assert text.count("| **VisionFM** |") == 1
    assert "CFP、OCT、FFA、B超、外眼、裂隙灯、MRI、UBM" in text
    assert "Stable Diffusion 生成模型" in text


def test_public_handoff_files_do_not_leak_local_or_transient_data() -> None:
    paths = [MANIFEST, CATALOG, VERIFY, HANDOFF]
    text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    forbidden = (
        "/data/LRT",
        "hf_",
        "confirm=",
        "signature=",
        "x-amz-",
        "release-assets.githubusercontent.com",
        "cdn-lfs",
        "xet-bridge",
        "cookie=",
        "token=",
    )
    lowered = text.lower()
    for value in forbidden:
        assert value.lower() not in lowered


def test_handoff_entrypoints_exist() -> None:
    for path in (CATALOG, VERIFY, HANDOFF):
        assert path.is_file()
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "docs/MODEL_WEIGHT_CATALOG.md" in readme
    assert "docs/DOWNLOAD_AND_VERIFY.md" in readme
    assert "catalog/download_manifest.csv" in readme
    assert "docs/EVALUATION_HANDOFF.md" in readme


def test_corrected_modalities_and_metric_provenance() -> None:
    rows = _rows()
    by_checkpoint = {row["checkpoint_id"]: row for row in rows}
    assert "corneal_photography" in by_checkpoint["eyeclip-default"]["modality"]
    assert "|CT|" not in f"|{by_checkpoint['eyeclip-default']['modality']}|"
    assert by_checkpoint["visionunite-default"]["modality"] == "CFP|text"

    flair = by_checkpoint["flair-default"]
    assert flair["impact_factor"] == "11.8"
    assert flair["impact_factor_year"] == "2024"
    assert flair["citescore"] == "26.6"
    assert flair["impact_factor_status"] == "verified"

    fmue = by_checkpoint["fmue-default"]
    assert fmue["impact_factor"] == "10.6"
    assert fmue["impact_factor_status"] == "value_verified_year_pending_jcr_confirmation"

    visionfm = by_checkpoint["visionfm-fundus"]
    assert visionfm["impact_factor"] == ""
    assert visionfm["impact_factor_status"] == "official_jif_not_publicly_confirmed"
    assert all(row["impact_factor_checked_at"] == "2026-07-13" for row in rows)


def test_download_status_dimensions_are_not_conflated() -> None:
    rows = _rows()
    downloaded = [row for row in rows if row["download_status"] == "downloaded"]
    assert len(downloaded) == 19
    assert all(row["source_provenance_status"] == "official_source_verified" for row in rows)
    assert all(row["local_integrity_status"] for row in rows)
    assert all(row["provider_integrity_status"] for row in rows)
    assert all(row["runtime_status"] == "not_tested" for row in rows)


def test_manifest_identity_fields_follow_registry() -> None:
    import yaml

    rows = {row["checkpoint_id"]: row for row in _rows()}
    models = {}
    for path in (ROOT / "registry" / "models").glob("*.yaml"):
        model = yaml.safe_load(path.read_text(encoding="utf-8"))
        models[model["model_id"]] = model
    for path in (ROOT / "registry" / "checkpoints").glob("*.yaml"):
        checkpoint = yaml.safe_load(path.read_text(encoding="utf-8"))
        row = rows[checkpoint["checkpoint_id"]]
        assert row["model_name"] == models[checkpoint["model_id"]]["model_name"]
        assert row["modality"] == "|".join(checkpoint["modalities"])
        assert row["artifact_type"] == checkpoint["artifact_type"]
        assert row["registry_verification_status"] == checkpoint["verification_status"]


def test_checkpoint_artifact_types_and_critical_classifications() -> None:
    rows = {row["checkpoint_id"]: row for row in _rows()}
    allowed = {
        "foundation_encoder",
        "vision_language_model",
        "task_checkpoint",
        "generative_model",
        "ablation_checkpoint",
        "multimodal_full_model",
    }
    assert {row["artifact_type"] for row in rows.values()} <= allowed
    assert rows["fmue-default"]["artifact_type"] == "task_checkpoint"
    assert rows["deretfound-sd-retina"]["artifact_type"] == "generative_model"
    assert rows["visionunite-default"]["artifact_type"] == "multimodal_full_model"
    assert rows["keepfit-half-flair-mmretinal-cfp"]["artifact_type"] == "ablation_checkpoint"
    visionfm_rows = [row for row in rows.values() if row["model_id"] == "visionfm"]
    assert all(row["local_asset_status"] == "legacy_asset_not_reverified" for row in visionfm_rows)
