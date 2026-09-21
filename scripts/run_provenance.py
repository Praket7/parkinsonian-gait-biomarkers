#!/usr/bin/env python3
"""Write a PHI-safe manifest for an analysis run.

Only paths, versions, timestamps, and cryptographic digests are recorded.
The script never opens files under data/raw and never records table contents.
The analysis itself may have used licensed row-level data in controlled
storage; the privacy fields below describe that distinction explicitly.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_commit(root: Path) -> str | None:
    if os.environ.get("ANALYSIS_RESULTS_COMMIT"):
        return os.environ["ANALYSIS_RESULTS_COMMIT"]
    try:
        return subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def git_tag(root: Path) -> str | None:
    if os.environ.get("RELEASE_TAG"):
        return os.environ["RELEASE_TAG"]
    try:
        return subprocess.run(
            ["git", "-C", str(root), "describe", "--tags", "--exact-match"],
            check=True, capture_output=True, text=True,
        ).stdout.strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


def config_value(config: Path, name: str) -> str | None:
    if not config.is_file():
        return None
    for line in config.read_text(encoding="utf-8").splitlines():
        key, sep, value = line.partition(":")
        if sep and key.strip() == name:
            return value.strip().strip("'\"")
    return None


def file_hashes(root: Path) -> dict[str, str]:
    """Hash only public aggregate artifacts, never local row-level tables."""
    results = root / "results" / "frozen"
    if not results.is_dir():
        return {}
    files = sorted(
        p for p in results.rglob("*")
        if p.is_file() and p.name != "run_provenance.json"
    )
    return {p.relative_to(root).as_posix(): sha256(p) for p in files}


def metadata_hashes(root: Path) -> dict[str, str]:
    metadata = root / "data" / "metadata"
    if not metadata.is_dir():
        return {}
    return {
        p.relative_to(root).as_posix(): sha256(p)
        for p in sorted(metadata.iterdir())
        if p.is_file()
    }


def build_manifest(root: Path, config: Path | None = None) -> dict[str, object]:
    config = config or root / "configs" / "analysis.yaml"
    dependency_lock = next(
        (root / name for name in ("requirements-lock.txt", "requirements.lock", "poetry.lock")
         if (root / name).is_file()),
        None,
    )
    requirements = root / "requirements.txt"
    config_digest = sha256(config) if config.is_file() else None
    lock_digest = sha256(dependency_lock) if dependency_lock else None
    return {
        "schema": "run-provenance-v3",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        # The results commit is deliberately an ancestor of this provenance
        # commit, avoiding a self-referential release SHA.
        "analysis_results_commit": git_commit(root),
        "release_tag": git_tag(root),
        "release_version": os.environ.get("RELEASE_TAG") or git_tag(root),
        "analysis_protocol_version": config_value(config, "analysis_protocol_version"),
        "report_generation_commit": os.environ.get("REPORT_GENERATION_COMMIT"),
        "analysis_version": config_value(config, "analysis_version"),
        "python_version": platform.python_version(),
        "config_sha256": config_digest,
        "dependency_lock_sha256": lock_digest,
        "config": {
            "path": config.relative_to(root).as_posix() if config.is_relative_to(root) else str(config),
            "sha256": config_digest,
        },
        "dependencies": {
            "lockfile": dependency_lock.relative_to(root).as_posix() if dependency_lock else None,
            "lockfile_sha256": lock_digest,
            "requirements_sha256": sha256(requirements) if requirements.is_file() else None,
        },
        "dataset_metadata_sha256": metadata_hashes(root),
        "aggregate_result_sha256": file_hashes(root),
        "privacy": {
            "provenance_script_read_row_level_data": False,
            "row_level_data_recorded_in_manifest": False,
            "row_level_data_published": False,
            "analysis_used_authorized_external_row_level_data": True,
            "note": "The analysis used authorized licensed source data in controlled storage. Only aggregate outputs and hashes are released; hashes do not permit recovery of source table contents.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default="results/frozen/run_provenance.json")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    output = (root / args.output).resolve() if not Path(args.output).is_absolute() else Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(build_manifest(root), indent=2) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
