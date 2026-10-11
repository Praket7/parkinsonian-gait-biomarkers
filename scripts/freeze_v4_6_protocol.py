#!/usr/bin/env python3
"""Freeze v4.6 analysis choices, historical inputs, and implementation before results."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "results/v4_6/protocol_manifest.json"
PROTOCOL_FILES = (
    "configs/v4_6_analysis.yaml",
    "docs/v4_6_preregistration.md",
)
PROTECTED_FILES = (
    "results/v4_1/frozen/v4_1_control_model.json",
    "src/v4_1/normative.py",
    "results/v4_3/v1_reconstruction_agreement.csv",
    "results/v4_3/v1_reconstruction_qc.json",
    "results/v4_5/h4b_endpoint_error_corrected.csv",
    "results/v4_5/AAN_v4_5_report.md",
)
IMPLEMENTATION_FILES = (
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
    "scripts/freeze_v4_6_protocol.py",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()


def build_manifest() -> dict:
    all_files = (*PROTOCOL_FILES, *PROTECTED_FILES, *IMPLEMENTATION_FILES)
    missing = [name for name in all_files if not (ROOT / name).exists()]
    if missing:
        raise FileNotFoundError(f"cannot freeze v4.6; missing files: {missing}")
    return {
        "schema": "v4.6-protocol-freeze-v1",
        "protocol": "v4.6.0",
        "files": {name: digest(ROOT / name) for name in PROTOCOL_FILES},
        "protected": {name: digest(ROOT / name) for name in PROTECTED_FILES},
        "implementation_hash_algorithm": "git_blob_sha1",
        "implementation": {name: git_blob_sha1(ROOT / name) for name in IMPLEMENTATION_FILES},
        "note": "Frozen before any v4.6 scientific result. Row-level authorized inputs remain outside Git.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write results/v4_6/protocol_manifest.json")
    args = parser.parse_args()
    manifest = build_manifest()
    if args.write:
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        print(MANIFEST.relative_to(ROOT))
    else:
        print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
