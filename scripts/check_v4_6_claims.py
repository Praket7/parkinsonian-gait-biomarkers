#!/usr/bin/env python3
"""Fail if v4.6 prose makes prespecified unsupported biomarker claims."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

PATTERNS = {
    "clinical_validation": r"\bclinically validated biomarker\b",
    "diagnosis": r"\bdiagnos(?:es|e|ing)\s+Parkinson",
    "progression": r"\btracks?\s+disease progression\b",
    "treatment_response": r"\btreatment response (?:is |was )?established\b",
    "short_term_reliability": r"\bshort[- ]term (?:test[- ]retest )?reliab(?:le|ility (?:is |was )?established)\b",
    "measurement_error": r"\bmeasurement error (?:is |was )?ruled out\b",
    "external_validation": r"\bexternally validated\b",
    "multisite_generalization": r"\bgeneralizes? across sites\b",
}


def find_unsupported_claims(text: str) -> list[str]:
    findings: list[str] = []
    for label, pattern in PATTERNS.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            findings.append(label)
    return findings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default="results/v4_6/v4_6_failure_mode_report.md", type=Path)
    args = parser.parse_args()
    if not args.path.exists():
        raise SystemExit(f"missing v4.6 report: {args.path}")
    findings = find_unsupported_claims(args.path.read_text())
    if findings:
        raise SystemExit("unsupported v4.6 claims: " + ", ".join(findings))
    print("v4.6 claim check passed")


if __name__ == "__main__":
    main()
