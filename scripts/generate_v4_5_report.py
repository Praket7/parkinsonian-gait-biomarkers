#!/usr/bin/env python3
"""Build the public v4.5 correction from aggregate data only."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def main() -> None:
    root = Path("results/v4_5")
    audit = json.loads((root / "source_audit.json").read_text())
    error = pd.read_csv(root / "h4b_endpoint_error_corrected.csv")
    h2 = pd.read_csv(root / "h2_favorable_fraction_corrected.csv")
    historical = pd.read_csv("results/v4_4/h4b_multipass_reliability.csv")
    rows = []
    for task in ("SelfPace", "HurriedPace"):
        a = error.set_index("task").loc[task]
        b = historical.set_index("task").loc[task]
        rows.append(f"| {task} | {int(a.n_paired)} | {b.icc_a1:.3f} ({b.icc_a1_ci_low:.3f} to {b.icc_a1_ci_high:.3f}) | {a.icc_bca_ci_low:.3f} to {a.icc_bca_ci_high:.3f} | {a.session_difference_sd:.3f} | {a.conditional_pass_resampling_sd_median:.3f} | {a.longitudinal_mdc95_equivalent:.3f} |")
    evidence = pd.DataFrame([
        {"claim": "Six-plus-month four-pass score stability", "status": "FAIL", "reason": "Both ICC lower confidence bounds remain below 0.80; real progression and state change may contribute"},
        {"claim": "Short-term four-pass test-retest reliability", "status": "NOT_ESTIMABLE", "reason": "No state-controlled, short-interval repeated visits"},
        {"claim": "Longitudinal clinical responsiveness", "status": audit["clinical_responsiveness_status"], "reason": audit["clinical_reason"]},
        {"claim": "CARE-PD eight-input score transport", "status": "NOT_ESTIMABLE", "reason": "No validated CARE-to-PKMAS analytical bridge for all eight inputs"},
        {"claim": "CARE-PD paired medication response of frozen score", "status": "NOT_ESTIMABLE", "reason": "Medication labels alone cannot validate an unbridged frozen score"},
    ])
    evidence.to_csv(root / "evidence_matrix.csv", index=False)
    document = f"""# AAN v4.5 scientific repair

This correction preserves the v4.1 score and historical v4.4 results. The [FDA dataset description](https://cdrh-rst.fda.gov/weargait-pd-longitudinal-multi-session-wearables-dataset-gait-parkinsons-disease) states that the minimum interval between sessions was six months, so the ICC estimates longitudinal score stability under changing clinical conditions. Short-term, state-controlled test–retest reliability is unmeasured. Neither task meets the frozen ICC lower-bound criterion of 0.80.

| Task | Paired participants | Six-plus-month ICC(A,1), percentile 95% CI | BCa 95% CI sensitivity | Paired difference SD | Four-pass conditional bootstrap SD, median | Longitudinal MDC95 equivalent |
| --- | ---: | --- | --- | ---: | ---: | ---: |
{chr(10).join(rows)}

The conditional bootstrap resamples the four observed passes, recomputes the median of each of the eight input features, then applies the SHA256-checked frozen model. It estimates pass-selection precision conditional on those passes. The paired-difference SD and its 1.96 multiple include disease change, medication/state differences, and measurement noise; they are **not** pure SEM or MDC for a stable clinical state. The v4.4 pass-score ANOVA's SEM, MDC95 and G coefficient used a mean-of-four residual rule and must not be used for this nonlinear endpoint. The pass-score variance components remain descriptive only. Three session files had only three valid passes; with so few exclusions, the selection effect cannot be estimated reliably.

## Clinical-source audit

The authorized longitudinal manifest lists {audit['manifest_rows']} files. The audit inventoried {audit['csv_files_inventoried']} CSVs, read {audit['task_csv_headers_read']} of {audit['task_files']} relevant SelfPace/HurriedPace headers, inspected {audit['session_mat_top_levels_read']} of {audit['session_mat_files_inventoried']} session MAT top levels, and read nested task fields in {audit['session_mat_structures_read']} structures. {audit['session_mat_recovered_from_synapse']} cloud MAT files required fresh temporary Synapse copies; {audit['failed_mat_count']} remained unreadable. MAT variables and task fields are recorded in [source_audit.json](source_audit.json). No verified repeated session-level MDS-UPDRS, medication dose/timing, or DBS variable was identified. {audit['v1_participants_matching_session1_identifiers']} session-1 identifiers match the V1 clinical table, but identifier overlap does not establish matched assessment dates and provides no session-2 clinical score. Clinical responsiveness remains `{audit['clinical_responsiveness_status']}`. The `ClinicalEvent` CSV field is a task annotation stream, not a clinical rating.

## CARE-PD transport and medication challenge

The released CARE-PD pickles include canonical SMPL pose/translation and some UPDRS/medication labels. These do not by themselves reproduce the eight frozen PKMAS gait inputs. All eight measurement equivalence gates remain unvalidated in [source_audit.json](source_audit.json). Accordingly, a frozen-score CARE-PD leave-one-center-out analysis and paired OFF/ON score responsiveness are `NOT_ESTIMABLE`. Running either analysis without that outcome-blind measurement bridge would manufacture comparability. The existing CARE-PD translation-speed associations remain separate exploratory evidence.

The v4.4 VA Seattle holdout shows association transport at one overlapping site. Its within-site standardized association does not test whether the absolute normative score is calibrated at that site, and one site cannot establish general transport.

## H2 reporting correction

Favorable calibration is now scored by distance to intercept 0 and slope 1. In the 100 stored repeated participant-grouped validations, the corrected fractions are:

| Unit | Slope closer to 1 | Intercept closer to 0 |
| --- | ---: | ---: |
| Participant | {h2.set_index('level').loc['participant','delta_calibration_slope_favorable_fraction']:.0%} | {h2.set_index('level').loc['participant','delta_calibration_intercept_favorable_fraction']:.0%} |
| Row | {h2.set_index('level').loc['row','delta_calibration_slope_favorable_fraction']:.0%} | {h2.set_index('level').loc['row','delta_calibration_intercept_favorable_fraction']:.0%} |

The ranking advantage remains; this correction does not establish better absolute clinical-score prediction. No severity outcome was used to choose a CARE-PD feature transform, site map, or reference threshold.

## Conclusion

The score has a validated WearGait eight-input reconstruction and reproducible incremental severity ranking. Its six-plus-month stability fails the frozen trait threshold. Short-term reliability, clinical responsiveness, and multi-center frozen-score transport require additional comparable measurements. HurriedPace may be investigated as a motor challenge in a future registered study, but this release does not claim a challenge-response biomarker.
"""
    (root / "AAN_v4_5_report.md").write_text(document)


if __name__ == "__main__":
    main()
