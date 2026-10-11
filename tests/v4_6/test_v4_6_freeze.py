from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs/v4_6_analysis.yaml"
PREREG = ROOT / "docs/v4_6_preregistration.md"
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


def test_v4_6_protocol_files_exist_before_analysis():
    missing = [str(path.relative_to(ROOT)) for path in (CONFIG, PREREG, MANIFEST) if not path.exists()]
    assert not missing, f"missing frozen v4.6 protocol files: {missing}"


def test_protocol_manifest_hashes_real_file_bytes():
    assert MANIFEST.exists(), "v4.6 protocol manifest must exist"
    manifest = json.loads(MANIFEST.read_text())
    assert manifest["schema"] == "v4.6-protocol-freeze-v1"
    for name, expected in manifest["files"].items():
        path = ROOT / name
        assert path.exists(), f"missing frozen file: {name}"
        assert sha256(path) == expected, f"hash mismatch: {name}"


def test_protocol_manifest_contains_locked_config_and_preregistration():
    assert MANIFEST.exists(), "v4.6 protocol manifest must exist"
    files = json.loads(MANIFEST.read_text())["files"]
    assert "configs/v4_6_analysis.yaml" in files
    assert "docs/v4_6_preregistration.md" in files


def test_manifest_locks_critical_v4_6_implementation_by_git_blob_identity():
    assert MANIFEST.exists(), "v4.6 protocol manifest must exist"
    manifest = json.loads(MANIFEST.read_text())
    implementation = manifest.get("implementation", {})
    assert REQUIRED_IMPLEMENTATION.issubset(implementation), REQUIRED_IMPLEMENTATION - set(implementation)
    for name in REQUIRED_IMPLEMENTATION:
        path = ROOT / name
        assert path.exists(), f"missing v4.6 implementation file: {name}"
        assert git_blob_sha1(path) == implementation[name], f"implementation hash mismatch: {name}"
