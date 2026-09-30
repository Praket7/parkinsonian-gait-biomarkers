#!/usr/bin/env python3
"""Release gate for the canonical, aggregate-only AAN submission bundle."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

try:
    from scripts.check_aan_submission_claims import check_values
except ModuleNotFoundError:
    from check_aan_submission_claims import check_values

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "report" / "AAN_FINAL_REPORT.md"
ABSTRACT = ROOT / "report" / "AAN_abstract.md"
MATRIX = ROOT / "report" / "AAN_FINAL_EVIDENCE_MATRIX.csv"
VALUES = ROOT / "report" / "AAN_submission_values.json"
REQUIRED = (
    REPORT, ABSTRACT, MATRIX, VALUES, ROOT / "report" / "AAN_prior_work_table.md",
    ROOT / "report" / "AAN_JUDGE_QA.md", ROOT / "report" / "AUTHORSHIP_AND_ASSISTANCE.md",
    ROOT / "report" / "AAN_bibliography.md",
)
FIGURES = tuple(ROOT / "report" / "figures" / "final" / f"figure_{i}_{name}.png" for i, name in (
    (1, "study_design"), (2, "reference_robustness"), (3, "incremental_validation"),
    (4, "measurement_validation"), (5, "longitudinal_stability"), (6, "evidence_ladder"),
))
ALLOWED_STATUS = {"SUPPORTED", "FAIL", "FAILED", "NOT_ESTIMABLE", "NOT ESTIMABLE", "INCOMPLETE", "NOT ESTABLISHED"}
UNSUPPORTED = re.compile(
    r"\b(?:is|was|are|were|proves?|demonstrates?)\s+(?:a\s+)?"
    r"(?:clinically validated|diagnostic biomarker|treatment-response biomarker|"
    r"reliable trait biomarker|validated across CARE-PD)\b",
    re.IGNORECASE,
)
OVERCLAIMED_VALIDATION = re.compile(
    r"survives independent validation(?: tests)?|"
    r"reproducible (?:severity-ranking )?information(?: about severity ranking)?",
    re.IGNORECASE,
)


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w]+(?:[’'-][\w]+)*\b", text))


def check(root: Path = ROOT) -> list[str]:
    errors = [f"missing required file: {path.relative_to(root)}" for path in REQUIRED if not path.is_file()]
    if errors:
        return errors
    abstract = ABSTRACT.read_text(encoding="utf-8")
    report = REPORT.read_text(encoding="utf-8")
    values = json.loads(VALUES.read_text(encoding="utf-8"))
    if word_count(abstract) > 300:
        errors.append(f"abstract has {word_count(abstract)} words, above the 300-word limit")
    if re.search(r"\bv3\.2\.4\b", abstract, re.IGNORECASE):
        errors.append("canonical abstract advertises the historical v3.2.4 analysis")
    if values.get("scientific_results_release") != "v4.5.1":
        errors.append("current scientific results release is not identified")
    if "v4.5" not in report or "252" not in report:
        errors.append("final report omits current v4.5 evidence or the 252-trial bridge")
    if not any(phrase in report.lower() for phrase in ("not a diagnosis", "not a clinical diagnosis", "does not diagnose")):
        errors.append("final report lacks a clear diagnostic boundary")
    if UNSUPPORTED.search(report):
        errors.append("final report contains an unsupported clinical claim")
    if OVERCLAIMED_VALIDATION.search(report) or OVERCLAIMED_VALIDATION.search(abstract):
        errors.append("canonical submission overstates validation or reproducibility")

    with MATRIX.open(newline="", encoding="utf-8") as handle:
        matrix = list(csv.DictReader(handle))
    if not matrix or not {"claim_id", "status", "source_file"} <= set(matrix[0]):
        errors.append("final evidence matrix is missing its required claim/source columns")
    elif any(row.get("status") not in ALLOWED_STATUS for row in matrix):
        errors.append("final evidence matrix contains an unrecognized status")
    elif any(not row.get("source_file") or not row.get("allowed_interpretation") or not row.get("prohibited_interpretation") for row in matrix):
        errors.append("final evidence matrix has a claim without source or interpretation boundaries")
    else:
        for row in matrix:
            for source in row["source_file"].split(";"):
                if not (root / source.strip()).is_file():
                    errors.append(f"evidence source file is missing: {source.strip()}")

    bibliography = (root / "report" / "AAN_bibliography.md").read_text(encoding="utf-8")
    cited = {number for group in re.findall(r"\[((?:\d+)(?:\s*,\s*\d+)*)\]", report)
             for number in re.findall(r"\d+", group)}
    referenced = set(re.findall(r"^(\d+)\.\s", bibliography, re.MULTILINE))
    if cited - referenced:
        errors.append(f"bibliography is missing cited references: {', '.join(sorted(cited - referenced))}")
    if not re.search(r"https://doi\.org/10\.", bibliography):
        errors.append("bibliography has no resolvable DOI links")

    required_values = (
        f"{values['primary']['standardized_effect']:.3f}",
        f"{values['primary']['q_value']:.4f}",
        str(values["analytical_bridge"]["matched_trials"]),
        f"{values['longitudinal_stability']['self_pace']['icc']:.3f}",
        f"{values['longitudinal_stability']['hurried_pace']['icc']:.3f}",
        f"{values['incremental_value']['participant_calibration_intercept_closer_to_zero_fraction']:.0%}",
    )
    if any(value not in report for value in required_values):
        errors.append("a required final-report numeric claim differs from its structured submission value")

    for path in FIGURES:
        if not path.is_file():
            errors.append(f"missing final figure: {path.relative_to(root)}")
    for source, text in ((REPORT, report), (ABSTRACT, abstract)):
        for target in re.findall(r"!?\[[^]]*\]\(([^)]+)\)", text):
            target = target.split("#", 1)[0]
            if not target or re.match(r"^(?:https?:|mailto:|#)", target):
                continue
            if not (source.parent / target).resolve().is_file():
                errors.append(f"broken link in {source.relative_to(root)}: {target}")
    authorship = (root / "report" / "AUTHORSHIP_AND_ASSISTANCE.md").read_text(encoding="utf-8").lower()
    if "ai-assisted" not in authorship or "original written work" not in authorship:
        errors.append("authorship and AI-assistance disclosure is incomplete")
    if abstract.strip() != (root / "abstract" / "abstract.txt").read_text(encoding="utf-8").strip():
        errors.append("standalone abstract copies do not match")
    if "v5.0.0-aan-submission" not in values.get("submission_release", ""):
        errors.append("submission release identifier is missing")
    if "historical" not in (root / "report" / "HISTORICAL_REPORTS.md").read_text(encoding="utf-8").lower():
        errors.append("historical-report guidance is missing")
    errors.extend(check_values(root))
    return errors


def main() -> int:
    errors = check()
    checks = [
        ("Canonical files", not any("missing required file" in error for error in errors)),
        ("Abstract word count", not any("abstract has" in error for error in errors)),
        ("Frozen value agreement", not any("expected" in error or "frozen" in error for error in errors)),
        ("Evidence matrix and statuses", not any("evidence matrix" in error for error in errors)),
        ("Figure and report links", not any("figure" in error or "link" in error for error in errors)),
        ("Clinical claim boundaries", not any("clinical claim" in error or "diagnostic boundary" in error for error in errors)),
        ("Authorship disclosure", not any("authorship" in error for error in errors)),
    ]
    print("AAN SUBMISSION QA\n=================")
    for label, passed in checks:
        print(f"{label:.<30} {'PASS' if passed else 'FAIL'}")
    if errors:
        print("\n" + "\n".join(errors))
        print("\nFINAL STATUS: FAIL")
        return 1
    print("\nFINAL STATUS: READY FOR STUDENT AUTHOR REVIEW")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
