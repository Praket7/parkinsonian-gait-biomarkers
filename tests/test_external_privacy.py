import csv
import json
from pathlib import Path

from scripts.qa_release_gate import _check_external_contract
from scripts.check_analysis_freeze import check_freeze


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=sorted(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _external_fixture(tmp_path: Path, status: str, output_status: str) -> tuple[Path, dict]:
    frozen = tmp_path / "results" / "frozen"
    _write_csv(frozen / "external_dataset_status.csv", [{"dataset": "mendeley_gait", "enabled": "True", "status": status}])
    for name in ("mendeley_cross_sectional_replication.csv", "mendeley_longitudinal_change.csv", "mendeley_medication_timing.csv"):
        _write_csv(frozen / name, [{"dataset": "mendeley_gait", "status": output_status}])
    return tmp_path, {"external_data": {"mendeley_gait": {"enabled": True}}}


def test_enabled_missing_external_source_requires_explicit_not_estimable(tmp_path: Path):
    root, config = _external_fixture(tmp_path, "NOT_ESTIMABLE_SOURCE_COMPONENT_MISSING", "NOT_ESTIMABLE")
    failures: list[str] = []
    _check_external_contract(root, config, failures)
    assert failures == []


def test_schema_stage_placeholder_cannot_ship_as_external_result(tmp_path: Path):
    root, config = _external_fixture(tmp_path, "OK", "SCHEMA_AUDIT_REQUIRED")
    failures: list[str] = []
    _check_external_contract(root, config, failures)
    assert any("non-final status" in failure for failure in failures)


def test_freeze_checks_protocol_and_release_identity(tmp_path: Path):
    (tmp_path / "configs").mkdir(parents=True)
    (tmp_path / "docs").mkdir()
    frozen = tmp_path / "results" / "frozen"
    frozen.mkdir(parents=True)
    (tmp_path / "configs" / "analysis.yaml").write_text("analysis_protocol_version: '3.2.1'\nrelease_version: 'v3.2.1'\n")
    (tmp_path / "configs" / "external_mappings.yaml").write_text("mapping_version: 'test'\n")
    (tmp_path / "docs" / "v3_2_analysis_freeze.md").write_text("protocol\n")
    (tmp_path / "docs" / "external_feature_mapping.md").write_text("mapping\n")
    digest = lambda path: __import__("hashlib").sha256(path.read_bytes()).hexdigest()
    (frozen / "analysis_freeze_manifest.json").write_text(json.dumps({
        "schema": "analysis-freeze-v1",
        "analysis_config_sha256": digest(tmp_path / "configs" / "analysis.yaml"),
        "analysis_protocol_sha256": digest(tmp_path / "docs" / "v3_2_analysis_freeze.md"),
            "feature_mapping_sha256": digest(tmp_path / "docs" / "external_feature_mapping.md"),
            "external_mappings_sha256": digest(tmp_path / "configs" / "external_mappings.yaml"),
    }))
    (frozen / "results.json").write_text(json.dumps({"analysis_protocol_version": "3.2.1", "release_version": "v3.2.1"}))
    (frozen / "run_provenance.json").write_text(json.dumps({"analysis_protocol_version": "3.2.1", "release_version": "v3.2.1"}))
    assert check_freeze(tmp_path) == []


def test_freeze_rejects_mismatched_release_identity(tmp_path: Path):
    (tmp_path / "configs").mkdir(parents=True)
    (tmp_path / "docs").mkdir()
    frozen = tmp_path / "results" / "frozen"
    frozen.mkdir(parents=True)
    config = tmp_path / "configs" / "analysis.yaml"
    protocol = tmp_path / "docs" / "v3_2_analysis_freeze.md"
    mapping = tmp_path / "docs" / "external_feature_mapping.md"
    config.write_text("analysis_protocol_version: '3.2.1'\nrelease_version: 'v3.2.1'\n")
    (tmp_path / "configs" / "external_mappings.yaml").write_text("mapping_version: 'test'\n")
    protocol.write_text("protocol\n")
    mapping.write_text("mapping\n")
    digest = lambda path: __import__("hashlib").sha256(path.read_bytes()).hexdigest()
    (frozen / "analysis_freeze_manifest.json").write_text(json.dumps({"schema": "analysis-freeze-v1", "analysis_config_sha256": digest(config), "analysis_protocol_sha256": digest(protocol), "feature_mapping_sha256": digest(mapping), "external_mappings_sha256": digest(tmp_path / "configs" / "external_mappings.yaml")}))
    (frozen / "results.json").write_text(json.dumps({"analysis_protocol_version": "3.2.1", "release_version": "v3.1.3"}))
    failures = check_freeze(tmp_path)
    assert "results and config release_version differ" in failures
