#!/usr/bin/env python3
"""Frozen-score, overlapping-site transport sensitivity for v4.4."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from run_v4_1_normative_validation import load
from src.stats_v3 import gee_association
from src.v4_1.normative import fit_reference, score


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", default="results/v4_4", type=Path)
    args = parser.parse_args()
    frame = load(args.source)
    controls = frame[frame.clinical_cohort.eq("control")].copy()
    pd_rows = frame[frame.clinical_cohort.eq("pd")].copy()
    rows = []
    for site in sorted(set(controls.site.dropna()).intersection(pd_rows.site.dropna())):
        reference = controls[~controls.site.eq(site)]
        target = pd_rows[pd_rows.site.eq(site)].copy()
        target["context_adjusted_gait_deviation_v1"] = score(target, fit_reference(reference))
        result = gee_association(target, "context_adjusted_gait_deviation_v1", minimum_participants=8)
        rows.append({"held_out_site": site, "reference_control_participants": int(reference.participant_id.nunique()),
                     "target_pd_participants": int(target.participant_id.nunique()), "estimability_status": result["status"],
                     "association_effect": result.get("effect"), "ci_low": result.get("ci_low"), "ci_high": result.get("ci_high"),
                     "p_value": result.get("p_value"), "association_status": "PASS" if result["status"] == "OK" and result["effect"] > 0 else "FAIL",
                     "transport_status": "INCOMPLETE", "reason": "ONE_OVERLAPPING_SITE_ONLY; CONTROL_REFERENCE_DERIVED_FROM_OTHER_SITE; NO_OUTCOME_TUNING; NOT_SUFFICIENT_FOR_GENERAL_TRANSPORT_CLAIM"})
    if not rows:
        rows.append({"held_out_site": "", "reference_control_participants": 0, "target_pd_participants": 0,
                     "estimability_status": "NOT_ESTIMABLE", "association_effect": "", "ci_low": "", "ci_high": "", "p_value": "",
                     "association_status": "INCOMPLETE", "transport_status": "NOT_ESTIMABLE", "reason": "NO_OVERLAPPING_AUTHORIZED_SITE_LABEL"})
    args.output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.output / "v4_4_site_transport.csv", index=False)


if __name__ == "__main__":
    main()
