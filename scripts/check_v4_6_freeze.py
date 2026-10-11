#!/usr/bin/env python3
"""Verify the frozen v4.6 protocol, historical inputs, and implementation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

from src.v4_1.normative import FROZEN_MODEL_SHA256, load_frozen_model

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "results/v4_6/protocol_manifest.json"
EXPECTED_CONFIG = {
    "protocol_version": "v4.6.0",
    "seed": 20261010,
    "participant_bootstrap_iterations": 2000,
    "control_reference_bootstrap_iterations": 2000,
    "direction_permutations": 10000,
    "primary_direction_statistic": "median",
    "multiple_testing": "holm",
    "primary_tasks": ["SelfPace", "HurriedPace"],
    "required_valid_passes_per_session": 4,
    "covariance_method": "sample",
    "zero_residual_rule": "exclude_and_count",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()


def check() -> list[str]:
    failures: list[str] = []
    if not MANIFEST.exists():
        return ["missing v4.6 protocol manifest"]
    try:
        manifest = json.loads(MANIFEST.read_text())
    except json.JSONDecodeError:
        return ["invalid v4.6 protocol manifest"]
    if manifest.get("schema") != "v4.6-protocol-freeze-v1":
        failures.append("invalid v4.6 freeze schema")
    for section in ("files", "protected"):
        for name, expected in manifest.get(section, {}).items():
            path = ROOT / name
            if not path.exists():
                failures.append(f"missing frozen file: {name}")
            elif digest(path) != expected:
                failures.append(f"v4.6 freeze mismatch: {name}")
    if manifest.get("implementation_hash_algorithm") != "git_blob_sha1":
        failures.append("invalid v4.6 implementation hash algorithm")
    implementation = manifest.get("implementation", {})
    if not implementation:
        failures.append("missing frozen v4.6 implementation identities")
    for name, expected in implementation.items():
        path = ROOT / name
        if not path.exists():
            failures.append(f"missing frozen implementation file: {name}")
        elif git_blob_sha1(path) != expected:
            failures.append(f"v4.6 implementation mismatch: {name}")
    config_path = ROOT / "configs/v4_6_analysis.yaml"
    if config_path.exists():
        config = yaml.safe_load(config_path.read_text())
        for key, expected in EXPECTED_CONFIG.items():
            if config.get(key) != expected:
                failures.append(f"locked config mismatch: {key}")
    else:
        failures.append("missing v4.6 config")
    model_path = ROOT / "results/v4_1/frozen/v4_1_control_model.json"
    if model_path.exists():
        if digest(model_path) != FROZEN_MODEL_SHA256:
            failures.append("frozen v4.1 model SHA256 contract changed")
        else:
            try:
                load_frozen_model(model_path)
            except (ValueError, OSError, json.JSONDecodeError) as error:
                failures.append(f"frozen v4.1 model contract invalid: {error}")
    else:
        failures.append("missing frozen v4.1 model")
    return failures


def main() -> None:
    failures = check()
    if failures:
        print("\n".join(failures))
        raise SystemExit(1)
    print("v4.6 freeze check passed")


if __name__ == "__main__":
    main()
