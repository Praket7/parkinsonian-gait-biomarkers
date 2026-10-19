from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.check_v4_6_freeze import check


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs/v4_6_analysis.yaml"
MANIFEST = ROOT / "results/v4_6/protocol_manifest.json"
REQUIRED_IMPLEMENTATION = {
    "src/v4_6/deviation_geometry.py",
    "src/v4_6/longitudinal_direction.py",
    "src/v4_6/score_agreement.py",
    "src/v4_6/reference_uncertainty.py",
    "scripts/run_v4_6_score_agreement.py",
    "scripts/run_v4_6_deviation_geometry.py",
    "scripts/run_v4_6_reference_uncertainty.py",
    "scripts/build_v4_6_report.py",
    "scripts/check_v4_6_claims.py",
    "scripts/run_v4_6_all.py",
    "scripts/check_v4_6_freeze.py",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()


def test_v4_6_machine_readable_protocol_files_exist():
    missing = [str(path.relative_to(ROOT)) for path in (CONFIG, MANIFEST) if not path.exists()]
    assert not missing, f"missing frozen v4.6 protocol files: {missing}"


def test_protocol_manifest_hashes_retained_file_bytes():
    assert MANIFEST.exists(), "v4.6 protocol manifest must exist"
    manifest = json.loads(MANIFEST.read_text())
    assert manifest["schema"] == "v4.6-protocol-freeze-v1"
    for name, expected in manifest["files"].items():
        path = ROOT / name
        assert path.exists(), f"missing frozen file: {name}"
        assert sha256(path) == expected, f"hash mismatch: {name}"


def test_protocol_manifest_locks_config_and_records_excluded_prose():
    assert MANIFEST.exists(), "v4.6 protocol manifest must exist"
    manifest = json.loads(MANIFEST.read_text())
    assert "configs/v4_6_analysis.yaml" in manifest["files"]
    assert "docs/v4_6_preregistration.md" in manifest.get("excluded_public_artifacts", [])


def test_manifest_locks_critical_v4_6_implementation_by_git_blob_identity():
    assert MANIFEST.exists(), "v4.6 protocol manifest must exist"
    manifest = json.loads(MANIFEST.read_text())
    implementation = manifest.get("implementation", {})
    assert REQUIRED_IMPLEMENTATION.issubset(implementation), REQUIRED_IMPLEMENTATION - set(implementation)
    for name in REQUIRED_IMPLEMENTATION:
        path = ROOT / name
        assert path.exists(), f"missing v4.6 implementation file: {name}"
        assert git_blob_sha1(path) == implementation[name], f"implementation hash mismatch: {name}"


def test_v4_6_freeze_checker_accepts_the_committed_retained_tree():
    assert check() == []
