#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_freeze(root: Path) -> list[str]:
    manifest_path = root / "results" / "frozen" / "analysis_freeze_manifest.json"
    if not manifest_path.is_file():
        return ["missing analysis freeze manifest"]
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ["invalid analysis freeze manifest"]
    failures: list[str] = []
    if manifest.get("schema") != "analysis-freeze-v1":
        failures.append("analysis freeze schema is not analysis-freeze-v1")
    paths = {"analysis_config_sha256": "configs/analysis.yaml", "analysis_protocol_sha256": "docs/v3_2_analysis_freeze.md", "feature_mapping_sha256": "docs/external_feature_mapping.md"}
    for key, relative in paths.items():
        path = root / relative
        if not path.is_file():
            failures.append(f"missing frozen input: {relative}")
        elif manifest.get(key) != sha(path):
            failures.append(f"POST_FREEZE_DEVIATION: {key}")

    config_path = root / "configs" / "analysis.yaml"
    results_path = root / "results" / "frozen" / "results.json"
    provenance_path = root / "results" / "frozen" / "run_provenance.json"
    if config_path.is_file():
        config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        expected = {"analysis_protocol_version": config.get("analysis_protocol_version"), "release_version": config.get("release_version")}
        for path, label in ((results_path, "results"), (provenance_path, "provenance")):
            if not path.is_file():
                continue
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                failures.append(f"invalid {label} manifest")
                continue
            for key, value in expected.items():
                if value is not None and payload.get(key) != value:
                    failures.append(f"{label} and config {key} differ")
    return failures


def main(root: str = ".") -> int:
    failures = check_freeze(Path(root).resolve())
    if failures:
        print("POST_FREEZE_DEVIATION: " + ", ".join(failures))
        return 1
    print("analysis freeze check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
