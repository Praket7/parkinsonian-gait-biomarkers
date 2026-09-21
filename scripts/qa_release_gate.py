#!/usr/bin/env python3
"""Fail-closed checks before treating results as scientific evidence.

This only audits files already present; it does not download, alter, or infer data.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
import subprocess
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.stats import bh_fdr
from src.stats_v3 import site_sign_consistency


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _number(value: str) -> float | None:
    try:
        value = value.strip()
        if not value or value.upper() in {"NA", "N/A", "NONE", "NAN"}:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _check_hashes(base: Path, provenance: dict[str, object], failures: list[str]) -> None:
    expected = provenance.get("aggregate_result_sha256") or {}
    if not isinstance(expected, dict):
        failures.append("provenance aggregate_result_sha256 is not a mapping")
        return
    actual = {}
    for rel in expected:
        path = base / rel
        if not path.is_file():
            failures.append(f"hashed aggregate is missing: {rel}")
        else:
            actual[rel] = _sha256(path)
            if actual[rel] != expected[rel]:
                failures.append(f"aggregate hash mismatch: {rel}")
    if set(actual) != set(expected):
        failures.append("provenance aggregate hash set is incomplete")


def _check_fdr(base: Path, failures: list[str]) -> None:
    path = base / "results" / "frozen" / "primary_associations.csv"
    rows = _csv(path)
    p = {i: _number(row.get("p_value", "")) for i, row in enumerate(rows)}
    q = bh_fdr(__import__("pandas").Series(p, dtype=float))
    for i, row in enumerate(rows):
        observed = _number(row.get("q_value", ""))
        if observed is not None and not math.isclose(observed, float(q.iloc[i]), rel_tol=1e-8, abs_tol=1e-10):
            failures.append(f"primary FDR q-value mismatch for {row.get('feature', i)}")
    if "speed_adjusted_p_value" in rows[0] if rows else False:
        p2 = __import__("pandas").Series({i: _number(row.get("speed_adjusted_p_value", "")) for i, row in enumerate(rows)}, dtype=float)
        q2 = bh_fdr(p2)
        for i, row in enumerate(rows):
            observed = _number(row.get("speed_adjusted_q_value", ""))
            if observed is not None and not math.isclose(observed, float(q2.iloc[i]), rel_tol=1e-8, abs_tol=1e-10):
                failures.append(f"speed-adjusted FDR q-value mismatch for {row.get('feature', i)}")


def _check_evidence(base: Path, config: dict, failures: list[str]) -> None:
    evidence = _csv(base / "results" / "frozen" / "feature_evidence_matrix.csv")
    primary = {row.get("feature"): row for row in _csv(base / "results" / "frozen" / "primary_associations.csv")}
    context = __import__("pandas").DataFrame(_csv(base / "results" / "frozen" / "context_robustness.csv"))
    reliability = _csv(base / "results" / "frozen" / "reliability.csv")
    features = [row.get("feature", "") for row in evidence]
    if len(features) != len(set(features)) or any(not feature for feature in features):
        failures.append("feature evidence matrix does not contain exactly one row per feature")
    for row in evidence:
        feature = row.get("feature")
        source = primary.get(feature, {})
        # Every displayed numeric evidence field must trace to the frozen GEE
        # association row; no result is accepted merely because it is present.
        for stored, source_name in (("severity_beta", "effect"), ("severity_q", "q_value"),
                                    ("speed_adjusted_beta", "speed_adjusted_effect"), ("speed_adjusted_q", "speed_adjusted_q_value"),
                                    ("bootstrap_same_sign_fraction", "bootstrap_same_sign_fraction"),
                                    ("task_interaction_p", "task_interaction_interaction_p_value"),
                                    ("site_interaction_p", "site_interaction_interaction_p_value")):
            actual, expected = _number(row.get(stored, "")), _number(source.get(source_name, ""))
            if actual is not None and expected is not None and not math.isclose(actual, expected, rel_tol=1e-8, abs_tol=1e-10):
                failures.append(f"evidence numeric trace mismatch for {feature} {stored}")
        consistency = site_sign_consistency(context, feature)
        stored_consistency = _number(row.get("leave_site_out_sign_consistency", ""))
        if stored_consistency is not None and not math.isclose(stored_consistency, consistency, rel_tol=1e-8, abs_tol=1e-10):
            failures.append(f"site consistency mismatch for {feature}")
        expected_site = "PASS" if consistency == 1 else ("NOT_ESTIMABLE" if math.isnan(consistency) else "FAIL")
        if row.get("site_robustness_status") != expected_site:
            failures.append(f"site robustness status mismatch for {feature}")
        rel_rows = [item for item in reliability if item.get("feature") == feature and item.get("task") == config["reliability"].get("trait_primary_task", "SP")]
        rel_values = [_number(item.get("icc_2_1", "")) for item in rel_rows]
        rel_values = [value for value in rel_values if value is not None]
        expected_reliability = "NOT_ESTIMABLE" if not rel_values else ("PASS" if max(rel_values) >= config["reliability"]["icc_candidate_threshold"] else "FAIL")
        if row.get("reliability_status") != expected_reliability:
            failures.append(f"reliability status mismatch for {feature}")
        q, adjusted_q = _number(source.get("q_value", "")), _number(source.get("speed_adjusted_q_value", ""))
        expected_severity = "PASS" if q is not None and q <= config["fdr_alpha"] else "FAIL"
        if row.get("severity_status") != expected_severity:
            failures.append(f"severity FDR status mismatch for {feature}")
        fraction = _number(source.get("bootstrap_same_sign_fraction", ""))
        expected_bootstrap = "PASS" if fraction is not None and fraction >= config["stability"]["minimum_direction_consistency"] else "FAIL"
        if row.get("bootstrap_status") != expected_bootstrap:
            failures.append(f"bootstrap status mismatch for {feature}")
        task_p = _number(source.get("task_interaction_interaction_p_value", ""))
        expected_task = "NOT_ESTIMABLE" if task_p is None else ("PASS" if task_p >= config["interaction_alpha"] else "FAIL")
        if row.get("task_robustness_status") != expected_task:
            failures.append(f"task interaction status mismatch for {feature}")
        if feature != "gait_speed":
            raw_effect, adjusted_effect = _number(source.get("effect", "")), _number(source.get("speed_adjusted_effect", ""))
            expected_speed = "NOT_ESTIMABLE" if None in (raw_effect, adjusted_effect, adjusted_q) else ("PASS" if math.copysign(1, raw_effect) == math.copysign(1, adjusted_effect) and adjusted_q <= config["speed_adjustment"]["fdr_alpha"] else "FAIL")
            if row.get("speed_status") != expected_speed:
                failures.append(f"speed-adjustment status mismatch for {feature}")
        mandatory = [row.get(key, "") for key in ("severity_status", "bootstrap_status", "speed_status", "task_robustness_status", "site_robustness_status", "reliability_status")]
        expected = "FAIL" if "FAIL" in mandatory else ("INCOMPLETE" if "NOT_ESTIMABLE" in mandatory else "PASS")
        if row.get("trait_status") != expected:
            failures.append(f"evidence status mismatch for {row.get('feature')}: expected {expected}")


def _check_numeric_trace(base: Path, failures: list[str]) -> None:
    path = base / "report" / "claim_evidence_matrix.csv"
    if not path.is_file():
        return
    frozen = base / "results" / "frozen"
    for claim in _csv(path):
        table_name = claim.get("table", "")
        source = frozen / table_name
        if not table_name or table_name.upper() in {"NA", "N/A"}:
            continue
        if not source.is_file():
            failures.append(f"claim {claim.get('claim_id')} references missing frozen table {table_name}")
            continue
        source_numbers = {_number(value) for row in _csv(source) for value in row.values()}
        source_numbers.discard(None)
        for field in ("effect", "p_value", "q_value"):
            value = _number(claim.get(field, ""))
            if value is not None and not any(math.isclose(value, candidate, rel_tol=2e-3, abs_tol=2e-4) for candidate in source_numbers):
                failures.append(f"claim {claim.get('claim_id')} {field} has no matching frozen numeric value")


def _check_public_headers(base: Path, failures: list[str]) -> None:
    forbidden = {"participant_id", "subject_id", "recording_id", "session_id"}
    for directory in (base / "results" / "frozen", base / "report"):
        if not directory.is_dir():
            continue
        for path in directory.rglob("*.csv"):
            with path.open(newline="", encoding="utf-8") as handle:
                headers = set(next(csv.reader(handle), []))
            leaked = sorted(headers & forbidden)
            if leaked:
                failures.append(f"row-level identifiers published in {path.relative_to(base)}: {', '.join(leaked)}")


def _git(base: Path, *args: str) -> str | None:
    try:
        return subprocess.run(["git", "-C", str(base), *args], check=True, capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _check_release_identity(base: Path, provenance: dict[str, object], failures: list[str]) -> None:
    current = _git(base, "rev-parse", "HEAD")
    analysis_commit = provenance.get("analysis_results_commit")
    if current and analysis_commit:
        try:
            subprocess.run(["git", "-C", str(base), "merge-base", "--is-ancestor", str(analysis_commit), current], check=True, capture_output=True)
        except (OSError, subprocess.CalledProcessError):
            failures.append("analysis_code_commit is not an ancestor of release commit")


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
            if provenance.get("schema") != "run-provenance-v3":
                failures.append("provenance schema is not run-provenance-v3")
            required_privacy = {
                "provenance_script_read_row_level_data": False,
                "row_level_data_recorded_in_manifest": False,
                "row_level_data_published": False,
                "analysis_used_authorized_external_row_level_data": True,
            }
            if any(provenance.get("privacy", {}).get(k) != v for k, v in required_privacy.items()):
                failures.append("provenance privacy wording is incomplete or inaccurate")
            if not provenance.get("analysis_results_commit"):
                failures.append("provenance lacks analysis_results_commit")
            _check_release_identity(base, provenance, failures)
        # Authorized files live outside the repository by design.  The public
        # release proves cohort flow from the aggregate table, not by exposing
        # an identifier-bearing derived audit table.
        feature_path = base / "results" / "v1_reference_walkway_clinical.csv"
        if (not raw.exists() or not any(p.is_file() for p in raw.rglob("*"))) and not (base / "results" / "frozen" / "participant_flow.csv").exists():
            failures.append("neither local raw input nor public aggregate participant flow is present")
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
        provenance_path = base / "results" / "frozen" / "run_provenance.json"
        if provenance_path.exists():
            provenance = json.loads(provenance_path.read_text())
            _check_hashes(base, provenance, failures)
        evidence_path = base / "results" / "frozen" / "feature_evidence_matrix.csv"
        if evidence_path.exists():
            config = yaml.safe_load((base / "configs" / "analysis.yaml").read_text()) or {}
            _check_evidence(base, config, failures)
        primary_path = base / "results" / "frozen" / "primary_associations.csv"
        if primary_path.exists():
            _check_fdr(base, failures)
        _check_numeric_trace(base, failures)
        _check_public_headers(base, failures)
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
