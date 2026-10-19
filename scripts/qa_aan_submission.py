#!/usr/bin/env python3
"""Release gate for the retained aggregate-only AAN submission artifacts."""
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
ABSTRACT = ROOT / "report" / "AAN_abstract.md"
MATRIX = ROOT / "report" / "AAN_FINAL_EVIDENCE_MATRIX.csv"
VALUES = ROOT / "report" / "AAN_submission_values.json"
APPENDIX = ROOT / "report" / "AAN_results_appendix.md"
REQUIRED = (ABSTRACT, MATRIX, VALUES, APPENDIX)
FIGURES = tuple(
    ROOT / "report" / "figures" / "final" / f"figure_{i}_{name}.png"
    for i, name in (
        (1, "study_design"),
        (2, "reference_robustness"),
        (3, "incremental_validation"),
        (4, "measurement_validation"),
        (5, "longitudinal_stability"),
        (6, "evidence_ladder"),
    )
)
ALLOWED_STATUS = {
    "SUPPORTED",
    "FAIL",
    "FAILED",
    "NOT_ESTIMABLE",
    "NOT ESTIMABLE",
    "INCOMPLETE",
    "NOT ESTABLISHED",
}
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


def _check_local_links(source: Path, text: str, root: Path, errors: list[str]) -> None:
    for target in re.findall(r"!?\[[^]]*\]\(([^)]+)\)", text):
        target = target.split("#", 1)[0]
        if not target or re.match(r"^(?:https?:|mailto:|#)", target):
            continue
        if not (source.parent / target).resolve().is_file():
            errors.append(f"broken link in {source.relative_to(root)}: {target}")


def check(root: Path = ROOT) -> list[str]:
    required = tuple(root / path.relative_to(ROOT) for path in REQUIRED)
    errors = [
        f"missing required file: {path.relative_to(root)}"
        for path in required
        if not path.is_file()
    ]
    if errors:
        return errors

    abstract_path = root / ABSTRACT.relative_to(ROOT)
    matrix_path = root / MATRIX.relative_to(ROOT)
    values_path = root / VALUES.relative_to(ROOT)
    appendix_path = root / APPENDIX.relative_to(ROOT)

    abstract = abstract_path.read_text(encoding="utf-8")
    appendix = appendix_path.read_text(encoding="utf-8")
    values = json.loads(values_path.read_text(encoding="utf-8"))

    if word_count(abstract) > 300:
        errors.append(f"abstract has {word_count(abstract)} words, above the 300-word limit")
    if re.search(r"\bv3\.2\.4\b", abstract, re.IGNORECASE):
        errors.append("canonical abstract advertises the historical v3.2.4 analysis")
    if values.get("scientific_results_release") != "v4.5.1":
        errors.append("current scientific results release is not identified")

    retained_text = f"{abstract}\n{appendix}"
    if UNSUPPORTED.search(retained_text):
        errors.append("retained submission text contains an unsupported clinical claim")
    if OVERCLAIMED_VALIDATION.search(retained_text):
        errors.append("retained submission text overstates validation or reproducibility")

    with matrix_path.open(newline="", encoding="utf-8") as handle:
        matrix = list(csv.DictReader(handle))
    if not matrix or not {"claim_id", "status", "source_file"} <= set(matrix[0]):
        errors.append("final evidence matrix is missing its required claim/source columns")
    elif any(row.get("status") not in ALLOWED_STATUS for row in matrix):
        errors.append("final evidence matrix contains an unrecognized status")
    elif any(
        not row.get("source_file")
        or not row.get("allowed_interpretation")
        or not row.get("prohibited_interpretation")
        for row in matrix
    ):
        errors.append("final evidence matrix has a claim without source or interpretation boundaries")
    else:
        for row in matrix:
            for source in row["source_file"].split(";"):
                if not (root / source.strip()).is_file():
                    errors.append(f"evidence source file is missing: {source.strip()}")

    for path in FIGURES:
        resolved = root / path.relative_to(ROOT)
        if not resolved.is_file():
            errors.append(f"missing final figure: {resolved.relative_to(root)}")

    _check_local_links(abstract_path, abstract, root, errors)
    _check_local_links(appendix_path, appendix, root, errors)

    standalone = root / "abstract" / "abstract.txt"
    if not standalone.is_file() or abstract.strip() != standalone.read_text(encoding="utf-8").strip():
        errors.append("standalone abstract copies do not match")
    if "v5.0.0-aan-submission" not in values.get("submission_release", ""):
        errors.append("submission release identifier is missing")

    errors.extend(check_values(root))
    return errors


def main() -> int:
    errors = check()
    checks = [
        ("Canonical files", not any("missing required file" in error for error in errors)),
        ("Abstract word count", not any("abstract has" in error for error in errors)),
        ("Frozen value agreement", not any("expected" in error or "frozen" in error for error in errors)),
        ("Evidence matrix and statuses", not any("evidence matrix" in error for error in errors)),
        ("Figure and retained-document links", not any("figure" in error or "link" in error for error in errors)),
        ("Clinical claim boundaries", not any("clinical claim" in error for error in errors)),
    ]
    print("AAN SUBMISSION QA\n=================")
    for label, passed in checks:
        print(f"{label:.<36} {'PASS' if passed else 'FAIL'}")
    if errors:
        print("\n" + "\n".join(errors))
        print("\nFINAL STATUS: FAIL")
        return 1
    print("\nFINAL STATUS: READY FOR STUDENT AUTHOR REVIEW")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
