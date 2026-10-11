from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "results/v4_6/protocol_manifest.json"
PROTECTED = {
    "results/v4_1/frozen/v4_1_control_model.json",
    "src/v4_1/normative.py",
    "results/v4_3/v1_reconstruction_agreement.csv",
    "results/v4_3/v1_reconstruction_qc.json",
    "results/v4_5/h4b_endpoint_error_corrected.csv",
    "results/v4_5/AAN_v4_5_report.md",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_manifest_protects_required_historical_inputs():
    assert MANIFEST.exists(), "v4.6 protocol manifest must exist before analysis"
    protected = json.loads(MANIFEST.read_text())["protected"]
    assert PROTECTED.issubset(protected), PROTECTED - set(protected)


def test_protected_historical_inputs_match_frozen_byte_hashes():
    assert MANIFEST.exists(), "v4.6 protocol manifest must exist before analysis"
    protected = json.loads(MANIFEST.read_text())["protected"]
    for name in PROTECTED:
        path = ROOT / name
        assert path.exists(), f"missing historical artifact: {name}"
        assert sha256(path) == protected[name], f"historical artifact changed: {name}"
