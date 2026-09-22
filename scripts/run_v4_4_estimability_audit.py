#!/usr/bin/env python3
"""Audit whether v4.4's clinical and site-transport estimands are authorized."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import pandas as pd

from run_v4_1_normative_validation import load


ANCHOR_TOKENS = ("updrs", "mds", "medication", "levodopa")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v1-root", required=True, type=Path)
    parser.add_argument("--longitudinal-root", required=True, type=Path)
    parser.add_argument("--output", default="results/v4_4", type=Path)
    args = parser.parse_args()
    v1 = load(args.v1_root)
    reference_sites = sorted(v1.loc[v1.clinical_cohort.eq("control"), "site"].dropna().unique())
    target_sites = sorted(v1.loc[v1.clinical_cohort.eq("pd"), "site"].dropna().unique())
    # The H4/H4b estimand is defined only for the two repeated SP/HP task files,
    # not unrelated exports sharing the directory.
    directory = args.longitudinal_root / "PD Participants" / "00-CSV files"
    files = sorted(directory.glob("*s[12]_SelfPace.csv")) + sorted(directory.glob("*s[12]_HurriedPace.csv"))
    if not files:
        raise SystemExit("no repeated task CSVs found")
    # These task files are a repeated export schema. One header is sufficient
    # for the field audit, and avoids forcing cloud-only pressure grids local.
    with files[0].open(newline="", encoding="utf-8", errors="replace") as handle:
        columns = sorted(next(csv.reader(handle)))
    anchor_fields = [column for column in columns if any(token in column.lower() for token in ANCHOR_TOKENS)]
    rows = [
        {"estimand": "internal_external_site_transport", "estimability_status": "NOT_ESTIMABLE" if not set(reference_sites).intersection(target_sites) else "OK",
         "reason": "NONOVERLAPPING_REFERENCE_AND_PD_SITE_LABELS" if not set(reference_sites).intersection(target_sites) else "OVERLAPPING_AUTHORIZED_SITE_LABELS",
         "reference_sites": "|".join(reference_sites), "target_sites": "|".join(target_sites)},
        {"estimand": "clinical_responsiveness", "estimability_status": "NOT_ESTIMABLE" if not anchor_fields else "REQUIRES_LINKAGE_AUDIT",
         "reason": "NO_REPEATED_CLINICAL_OR_MEDICATION_FIELDS_IN_LONGITUDINAL_WALKWAY_CSVS" if not anchor_fields else "POTENTIAL_ANCHOR_FIELDS_REQUIRE_LINKAGE_AUDIT",
         "reference_sites": "", "target_sites": ""},
    ]
    args.output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.output / "v4_4_estimability_audit.csv", index=False)
    (args.output / "v4_4_estimability_audit.json").write_text(json.dumps({
        "protocol": "4.4.0", "longitudinal_task_csv_count": len(files), "header_schema_probe_csv_count": 1, "longitudinal_anchor_like_fields": anchor_fields,
        "reference_sites": reference_sites, "pd_sites": target_sites,
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
