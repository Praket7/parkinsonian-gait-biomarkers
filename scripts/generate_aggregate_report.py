#!/usr/bin/env python3
"""Generate cautious public report text from frozen aggregate outputs only."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def _number(value: Any, digits: int = 3) -> str:
    try:
        return f"{float(value):.{digits}g}"
    except (TypeError, ValueError):
        return "not reported"


def _manifest(root: Path) -> dict[str, Any]:
    path = root / "results" / "frozen" / "results.json"
    if not path.is_file():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def _primary_rows(root: Path) -> list[dict[str, str]]:
    for path in (root / "results" / "frozen" / "primary_associations.csv", root / "results" / "primary_associations.csv"):
        if path.is_file():
            with path.open(newline="", encoding="utf-8") as handle:
                return list(csv.DictReader(handle))
    return []


def _primary_summary(root: Path) -> list[str]:
    lines: list[str] = []
    for row in _primary_rows(root):
        feature = row.get("feature") or row.get("metric") or row.get("variable")
        if not feature or feature.lower() in {"participant_id", "session_id"}:
            continue
        effect = row.get("estimate") or row.get("beta") or row.get("effect") or row.get("spearman_rho")
        p_value = row.get("p_value") or row.get("p")
        q_value = row.get("q_value") or row.get("q") or row.get("fdr_q")
        details = [f"effect={_number(effect)}"] if effect is not None else []
        if p_value is not None:
            details.append(f"p={_number(p_value)}")
        if q_value is not None:
            details.append(f"q={_number(q_value)}")
        lines.append(f"- `{feature}`: {', '.join(details) or 'aggregate estimate reported'}")
    return lines


def _frozen_rows(root: Path, name: str) -> list[dict[str, str]]:
    path = root / "results" / "frozen" / name
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _table_summary(root: Path, name: str, label: str) -> list[str]:
    """Summarize allow-listed aggregate columns, never arbitrary row values."""
    rows = _frozen_rows(root, name)
    if not rows:
        return [f"- {label}: table not present in the frozen bundle."]
    lines: list[str] = []
    for row in rows:
        subject = row.get("feature") or row.get("metric") or row.get("cohort") or row.get("task") or row.get("source") or row.get("control")
        if not subject or subject.lower() in {"participant_id", "session_id", "subject_id"}:
            continue
        fields = []
        for key in ("status", "classification", "evidence_status", "icc_2_1", "rho", "spearman_rho", "effect", "estimate", "p_value", "q_value", "ci_low", "ci_high", "n", "n_pairs", "n_trials"):
            if row.get(key) not in (None, ""):
                fields.append(f"{key}={_number(row[key]) if key not in {'status', 'classification', 'evidence_status'} else row[key]}")
        lines.append(f"- `{subject}`: {', '.join(fields) or 'aggregate row reported'}")
    return lines or [f"- {label}: no safe aggregate rows found."]


def render(root: Path) -> tuple[str, str]:
    data = _manifest(root)
    version = data.get("analysis_version", "not reported")
    status = data.get("status", "not reported")
    trait_features = data.get("trait_features") or []
    n_rows = data.get("n_primary_rows", "not reported")
    n_participants = data.get("n_primary_participants", "not reported")
    longitudinal = data.get("longitudinal") or []
    limits = data.get("limits") or []
    primary = _primary_summary(root) or ["- Feature-level aggregate association table was not present in the frozen bundle."]
    reliability = _table_summary(root, "reliability.csv", "Frozen reliability table") if _frozen_rows(root, "reliability.csv") else [f"- `{item.get('feature', 'unknown')}`: ICC(2,1)={_number(item.get('icc_2_1'))}" for item in longitudinal if isinstance(item, dict)] or ["- Longitudinal reliability estimates were not reported."]
    evidence = _table_summary(root, "feature_evidence_matrix.csv", "Feature evidence matrix")
    contact = _table_summary(root, "contact_validation.csv", "Contact validation")
    cohort = _table_summary(root, "carepd_cohort_results.csv", "CARE-PD cohort results")
    medication = _table_summary(root, "medication_sensitivity.csv", "Medication-state sensitivity")
    controls = _table_summary(root, "negative_controls.csv", "Negative controls")
    limit_lines = [f"- {item}" for item in limits] or ["- Additional limitations were not reported."]
    report = f"""# Parkinsonian gait biomarkers: aggregate analysis report

Analysis version: `{version}`  
Frozen status: `{status}`

## Scope

This report is generated from frozen aggregate outputs. It does not contain
participant identifiers or row-level observations. The primary bundle contains
{n_rows} analyzed rows from {n_participants} participants, as reported by the
frozen manifest.

## Main result

The implemented pipeline identified {len(trait_features)} feature(s) meeting
its current strict trait rule: {', '.join(f'`{x}`' for x in trait_features) or 'none reported'}.
This is a statement about the implemented evidence pipeline, not proof that
every unimplemented evidence path was negative.

## Aggregate associations

{chr(10).join(primary)}

## Reliability summary

{chr(10).join(reliability)}

## Feature evidence matrix

{chr(10).join(evidence)}

## Contact validation

{chr(10).join(contact)}

## External translation check

These are cohort-specific translation-speed checks, not full matched-feature
replication.

{chr(10).join(cohort)}

## Medication-state sensitivity

{chr(10).join(medication)}

## Negative controls

{chr(10).join(controls)}

## Limitations and deviations

{chr(10).join(limit_lines)}

Do not interpret this report as diagnostic, causal, treatment, or clinical-use
evidence. Regenerate it after every authorized analysis run.
"""
    abstract = (
        f"Parkinsonian gait biomarkers (analysis v{version}). We analyzed {n_rows} frozen aggregate rows from {n_participants} participants. "
        f"The implemented pipeline classified {len(trait_features)} feature(s) as meeting its current strict trait rule ({', '.join(trait_features) or 'none reported'}). "
        "This result is not equivalent to a true negative for evidence paths that were not estimable or not implemented. "
        "CARE-PD was analyzed as cohort-specific translation-speed evidence, not full external feature replication. "
        "These aggregate results do not support diagnostic, causal, treatment, or clinical-use claims.\n"
    )
    return report, abstract


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--check", action="store_true", help="render and validate without writing files")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    report, abstract = render(root)
    if any(token in (report + abstract).lower() for token in ("participant_id", "session_id", "subject_id")):
        raise SystemExit("generated text contains a forbidden identifier field")
    if args.check:
        print("aggregate report check passed")
        return 0
    report_path = root / "report" / "AAN_report.md"
    abstract_path = root / "abstract" / "abstract.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    abstract_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    abstract_path.write_text(abstract, encoding="utf-8")
    print(report_path)
    print(abstract_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
