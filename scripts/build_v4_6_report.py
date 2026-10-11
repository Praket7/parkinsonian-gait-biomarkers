#!/usr/bin/env python3
"""Build the aggregate-only v4.6 failure-mode report and machine summary."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def _fmt(value, digits=3) -> str:
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return "NA"


def render_report(summary: dict) -> str:
    historical = summary.get("historical_score", {})
    analytical = summary.get("score_level_analytical_agreement", {})
    direction = summary.get("longitudinal_direction_conservation", {})
    reference = summary.get("healthy_reference_uncertainty", {})
    boundaries = summary.get("claim_boundaries", {})
    lines = [
        "# v4.6 biomarker failure-mode analysis",
        "",
        "## Scope",
        "",
        "v4.6 preserves the frozen v4.1 gait score and the historical v4.5 conclusion. "
        "The prior endpoint failed its prespecified six-plus-month longitudinal stability criterion. "
        "This extension asks where that instability enters the evidence chain rather than redefining the endpoint.",
        "",
        "The analyses separate final-score analytical agreement, within-person multivariate pattern conservation, "
        "and uncertainty from estimating the healthy reference. These are different evidence layers and are not interchangeable.",
        "",
        "## Final-score analytical agreement",
        "",
    ]
    if analytical:
        lines += [
            f"Matched trials: {analytical.get('n', 'NA')}. ICC(A,1) was {_fmt(analytical.get('icc_a1'))}, "
            f"CCC was {_fmt(analytical.get('ccc'))}, MAE was {_fmt(analytical.get('mae'))}, and RMSE was {_fmt(analytical.get('rmse'))}.",
            "These statistics describe agreement between the same frozen score calculated from PKMAS-derived versus independently reconstructed walkway inputs. "
            "They do not establish clinical utility or cross-device transport.",
        ]
    else:
        lines.append("No controlled matched-trial score-agreement result has been supplied to this report builder.")
    lines += ["", "## Six-plus-month deviation-pattern conservation", ""]
    if direction:
        for task in ("SelfPace", "HurriedPace"):
            item = direction.get(task)
            if not item:
                continue
            ci = item.get("bootstrap_ci", [None, None])
            lines.append(
                f"{task}: {item.get('n', 'NA')} paired participants, median precision-metric cosine "
                f"{_fmt(item.get('median_precision_cosine'))}, participant-bootstrap 95 percent interval "
                f"{_fmt(ci[0])} to {_fmt(ci[1])}, Holm-adjusted permutation p {_fmt(item.get('holm_p'), 4)}."
            )
        lines.append(
            "Directional similarity is interpreted as conservation of the multivariate gait-deviation pattern across a long interval. "
            "It is not short-term state-controlled test-retest reliability."
        )
    else:
        lines.append("No controlled longitudinal direction result has been supplied to this report builder.")
    lines += ["", "## Healthy-reference estimation uncertainty", ""]
    if reference:
        for task in ("SelfPace", "HurriedPace"):
            item = reference.get(task)
            if not item:
                continue
            interval = item.get("icc_reference_interval", [None, None])
            lines.append(
                f"{task}: median reference-resampled ICC {_fmt(item.get('icc_median'))}, with healthy-reference "
                f"2.5th to 97.5th percentile {_fmt(interval[0])} to {_fmt(interval[1])}."
            )
        lines.append(
            "These percentiles quantify healthy-reference estimation sensitivity. They are not participant-sampling confidence intervals, "
            "and they do not isolate biological state change from measurement noise."
        )
    else:
        lines.append("No controlled healthy-reference bootstrap result has been supplied to this report builder.")
    lines += [
        "",
        "## Evidence boundaries",
        "",
        f"Short-term state-controlled reliability: {boundaries.get('short_term_reliability', 'NOT_ESTIMABLE')}.",
        f"Clinical responsiveness: {boundaries.get('clinical_responsiveness', 'NOT_ESTIMABLE')}.",
        f"Independent full-score external transport: {boundaries.get('external_full_score_transport', 'NOT_ESTIMABLE')}.",
        "",
        "v4.6 does not establish diagnosis, treatment response, progression tracking, clinically meaningful change thresholds, or general multi-site validation.",
        "The frozen historical score remains unchanged.",
        "",
    ]
    return "\n".join(lines)


def load_summary(output: Path) -> dict:
    summary_path = output / "v4_6_summary.json"
    if summary_path.exists():
        return json.loads(summary_path.read_text())
    return {
        "historical_score": {"status": "UNCHANGED", "longitudinal_interval": "six_plus_months"},
        "claim_boundaries": {
            "short_term_reliability": "NOT_ESTIMABLE",
            "clinical_responsiveness": "NOT_ESTIMABLE",
            "external_full_score_transport": "NOT_ESTIMABLE",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="results/v4_6", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    summary = load_summary(args.output)
    (args.output / "v4_6_failure_mode_report.md").write_text(render_report(summary) + "\n")
    (args.output / "v4_6_machine_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
