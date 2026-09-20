#!/usr/bin/env python3
"""Fail-closed checks before treating results as scientific evidence.

This only audits files already present; it does not download, alter, or infer data.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import yaml


def _ids(path: Path) -> set[str]:
    import csv

    with path.open(newline="") as handle:
        rows = csv.DictReader(handle)
        return {row["participant_id"] for row in rows if row.get("participant_id")}


def main(root: str) -> int:
    base = Path(root)
    failures: list[str] = []
    raw = base / "data" / "raw"
    manifest_path = base / "results" / "frozen" / "results.json"
    if not manifest_path.exists():
        failures.append("missing results/frozen/results.json")
    else:
        manifest = json.loads(manifest_path.read_text())
        if manifest.get("status") != "analysis_complete":
            failures.append("frozen manifest does not report analysis_complete")
        config_path = base / "configs" / "analysis.yaml"
        if not config_path.exists() or manifest.get("analysis_version") != (yaml.safe_load(config_path.read_text()) or {}).get("analysis_version"):
            failures.append("analysis version differs between config and manifest")
        for name in ("primary_associations.csv", "feature_evidence_matrix.csv", "reliability.csv", "contact_validation.csv", "context_robustness.csv", "carepd_cohort_results.csv", "medication_sensitivity.csv", "negative_controls.csv", "participant_flow.csv"):
            if not (base / "results" / "frozen" / name).exists():
                failures.append(f"missing aggregate output {name}")
        if not (base / "requirements-lock.txt").exists():
            failures.append("missing requirements-lock.txt")
        provenance_path = base / "results" / "frozen" / "run_provenance.json"
        if not provenance_path.exists():
            failures.append("missing aggregate run provenance")
        else:
            provenance = json.loads(provenance_path.read_text())
            if provenance.get("analysis_version") != manifest.get("analysis_version"):
                failures.append("provenance and result manifest versions differ")
        # Authorized files live outside the repository by design.  Require an
        # auditable derived table instead of requiring a redistributable copy.
        feature_path = base / "results" / "v1_reference_walkway_clinical.csv"
        if (not raw.exists() or not any(p.is_file() for p in raw.rglob("*"))) and not feature_path.exists():
            failures.append("neither local raw input nor authorized derived audit table is present")
        if feature_path.exists() and feature_path.stat().st_size:
            import csv

            with feature_path.open(newline="") as handle:
                rows = list(csv.DictReader(handle))
            required = {"participant_id", "task"}
            if rows and not required.issubset(rows[0]):
                failures.append("feature table lacks participant_id/task")
            keys = [(r.get("participant_id"), r.get("session_id"), r.get("task")) for r in rows]
            if len(keys) != len(set(keys)):
                failures.append("duplicate participant/site/session/task keys")
    # If a user supplies explicit split CSVs, enforce participant grouping.
    split_paths = list(base.glob("**/*[Tt]rain*.csv")) + list(base.glob("**/*[Tt]est*.csv"))
    splits = {p.name: _ids(p) for p in split_paths}
    train = set().union(*(v for k, v in splits.items() if "train" in k.lower()))
    test = set().union(*(v for k, v in splits.items() if "test" in k.lower()))
    overlap = train & test
    if overlap:
        failures.append(f"participant leakage across train/test ({len(overlap)} IDs)")
    if failures:
        print("QA BLOCKED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("QA PASS: release gate checks passed")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    raise SystemExit(main(parser.parse_args().root))
