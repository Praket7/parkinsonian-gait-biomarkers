from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs/v4_6_analysis.yaml"
PREREG = ROOT / "docs/v4_6_preregistration.md"
MANIFEST = ROOT / "results/v4_6/protocol_manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
