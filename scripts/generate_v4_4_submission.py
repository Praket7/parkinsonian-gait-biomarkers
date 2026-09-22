#!/usr/bin/env python3
"""Generate v4.4 public-safe evidence material from aggregate-only outputs."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="results/v4_4", type=Path)
    parser.add_argument("--output", default="results/v4_4", type=Path)
    args = parser.parse_args()
    reliability = pd.read_csv(args.input / "h4b_multipass_reliability.csv")
    audit = pd.read_csv(args.input / "v4_4_estimability_audit.csv")
    transport = pd.read_csv(args.input / "v4_4_site_transport.csv")
    args.output.mkdir(parents=True, exist_ok=True)
    evidence = pd.concat([
        pd.DataFrame([{"claim": "V4.3 raw-to-PKMAS analytical bridge", "status": "PASS", "evidence": "All eight V1 inputs passed locked analytical-equivalence gates on 252 matched trials.", "interpretation": "Raw walkway reconstruction is analytically valid."},
                      {"claim": "V4.3 frozen single-score test-retest reliability", "status": "FAIL", "evidence": "Self-paced ICC(A,1)=0.707 (CI 0.462 to 0.844); hurried ICC(A,1)=0.390 (CI 0.073 to 0.657).", "interpretation": "The original score is not a qualified stable trait biomarker."}]),
        reliability.assign(claim="V4.4 four-pass median protocol reliability", status=reliability.test_retest_status,
                           evidence=lambda x: x.apply(lambda r: f"{r.task}: ICC(A,1)={r.icc_a1:.3f}, 95% CI {r.icc_a1_ci_low:.3f} to {r.icc_a1_ci_high:.3f}; MDC95={r.mdc95:.3f}.", axis=1),
                           interpretation="A new four-pass median endpoint is not qualified unless its lower CI reaches 0.80.")[["claim", "status", "evidence", "interpretation"]],
        transport.assign(claim="v4.4 overlapping-site transport sensitivity", status=transport.transport_status,
                         evidence=lambda x: x.apply(lambda r: f"{r.held_out_site}: effect={r.association_effect:.3f}, 95% CI {r.ci_low:.3f} to {r.ci_high:.3f}; {r.reason}", axis=1),
                         interpretation="A single overlapping-site holdout is a transport sensitivity, not a general transport pass.")[["claim", "status", "evidence", "interpretation"]],
        audit[audit.estimand.eq("clinical_responsiveness")].assign(claim="clinical responsiveness", status=lambda x: x.estimability_status,
                     evidence=audit.reason, interpretation="Authorization and schema boundary; no substitute analysis was fitted.")[["claim", "status", "evidence", "interpretation"]],
    ], ignore_index=True)
    evidence.to_csv(args.output / "v4_4_evidence_matrix.csv", index=False)
    figure_dir = args.output / "figures"
    figure_dir.mkdir(exist_ok=True)
    labels = ["Analytical\nvalidity", "Original\nreliability", "Four-pass\nreliability", "Clinical\nresponsiveness", "Site\ntransport"]
    states = ["PASS", "FAIL", "FAIL", "NOT_ESTIMABLE", "INCOMPLETE"]
    colors = {"PASS": "#238b45", "FAIL": "#cb181d", "NOT_ESTIMABLE": "#636363", "INCOMPLETE": "#b8860b"}
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.bar(range(len(labels)), [1] * len(labels), color=[colors[s] for s in states], width=.72)
    for index, state in enumerate(states): ax.text(index, .5, state.replace("_", "\n"), ha="center", va="center", color="white", weight="bold", fontsize=10)
    ax.set_xticks(range(len(labels)), labels); ax.set_ylim(0, 1); ax.set_yticks([])
    ax.set_title("v4.4 claim ladder: measure accurately, then earn each clinical claim")
    for spine in ax.spines.values(): spine.set_visible(False)
    fig.tight_layout(); fig.savefig(figure_dir / "v4_4_claim_ladder.png", dpi=220); plt.close(fig)
    rows = "\n".join(f"| {r.claim} | `{r.status}` | {r.evidence} |" for r in evidence.itertuples())
    h4b = "\n".join(f"| {r.task} | {int(r.n_participants)} | {r.icc_a1:.3f} | {r.icc_a1_ci_low:.3f} to {r.icc_a1_ci_high:.3f} | {r.mdc95:.3f} | `{r.test_retest_status}` |" for r in reliability.itertuples())
    report = f"""# AAN v4.4 measurement-error and responsiveness extension

## Bottom line

v4.4 makes the project more defensible by testing the proposed protocol rescue without changing the frozen v4.1 score, model, or v4.3 result. The four-pass, featurewise-median endpoint was estimable but did not meet the preregistered lower-95%-CI reliability criterion of 0.80. This is evidence against the proposed rescue under this protocol, not a reason to relax the criterion.

## New H4b protocol result

| Task | Paired participants | ICC(A,1) | 95% bootstrap CI | MDC95 | Status |
| --- | ---: | ---: | --- | ---: | --- |
{h4b}

The score's analytical reconstruction remains validated. Its single-score and four-pass session-aggregate reliability are separate claims, and neither endpoint qualifies as a stable trait biomarker under the frozen 0.80 lower-bound rule.

## Claim ladder

![v4.4 claim ladder](figures/v4_4_claim_ladder.png)

| Claim | Status | Evidence |
| --- | --- | --- |
{rows}

## What this does and does not establish

The project now documents analytical validity, single-score reliability, a prespecified multi-pass protocol attempt, absolute measurement error, and the precise authorized-data boundaries for site transport and clinical responsiveness. It does not claim diagnostic performance, treatment response, causal change, or clinical utility. Repeated MDS-UPDRS Part III and medication-timing data linked to each longitudinal gait session are required before responsiveness or an anchor-based clinically meaningful change can be estimated.
"""
    (args.output / "AAN_v4_4_report.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
