#!/usr/bin/env python3
"""Freeze v4.6 analysis choices and protected historical inputs before results."""
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


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_manifest() -> dict:
    missing = [name for name in (*PROTOCOL_FILES, *PROTECTED_FILES) if not (ROOT / name).exists()]
    if missing:
        raise FileNotFoundError(f"cannot freeze v4.6; missing files: {missing}")
    return {
        "schema": "v4.6-protocol-freeze-v1",
        "protocol": "v4.6.0",
        "files": {name: digest(ROOT / name) for name in PROTOCOL_FILES},
        "protected": {name: digest(ROOT / name) for name in PROTECTED_FILES},
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
