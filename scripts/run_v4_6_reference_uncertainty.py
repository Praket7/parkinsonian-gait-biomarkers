#!/usr/bin/env python3
"""Propagate healthy-control reference sampling uncertainty through v4.6 endpoints."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import yaml

from check_v4_6_freeze import check
from src.v4_1.normative import load_frozen_model
from src.v4_6.reference_uncertainty import reference_bootstrap, summarize_reference_uncertainty
from src.walkway import load_walkway_metrics
from src.weargait_clinical import join_clinical_features, load_v1_clinical


def _controls(v1_root: Path) -> pd.DataFrame:
    walkway = load_walkway_metrics(v1_root / "Walkway-derived metrics" / "PKMAS Walkway Gait Metrics - HP+SP.csv")
    clinical = load_v1_clinical(
        v1_root / "PD - Demographic+Clinical - datasetV1.csv",
        v1_root / "CONTROLS - Demographic+Clinical - datasetV1.csv",
    )
    full = join_clinical_features(walkway, clinical)
    return full.loc[full.clinical_cohort.eq("control")].copy()


def _update_summary(path: Path, summary_table: pd.DataFrame) -> None:
    current = json.loads(path.read_text()) if path.exists() else {}
    current.setdefault("historical_score", {"status": "UNCHANGED", "longitudinal_interval": "six_plus_months"})
    payload = {}
    for row in summary_table.itertuples(index=False):
        payload[row.task] = {
            "icc_median": row.icc_a1_median,
            "icc_reference_interval": [row.icc_a1_reference_p025, row.icc_a1_reference_p975],
            "median_precision_cosine_median": row.median_precision_cosine_median,
            "median_precision_cosine_reference_interval": [
                row.median_precision_cosine_reference_p025,
                row.median_precision_cosine_reference_p975,
            ],
            "uncertainty_type": "healthy_reference_estimation",
        }
    current["healthy_reference_uncertainty"] = payload
    current.setdefault("claim_boundaries", {
        "short_term_reliability": "NOT_ESTIMABLE",
        "clinical_responsiveness": "NOT_ESTIMABLE",
        "external_full_score_transport": "NOT_ESTIMABLE",
    })
    path.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v1-root", required=True, type=Path)
    parser.add_argument("--endpoints", type=Path, default=None, help="controlled local v4.4 four-pass endpoint table")
    parser.add_argument("--config", type=Path, default=Path("configs/v4_6_analysis.yaml"))
    parser.add_argument("--model", type=Path, default=Path("results/v4_1/frozen/v4_1_control_model.json"))
    parser.add_argument("--output", type=Path, default=Path("results/v4_6"))
    args = parser.parse_args()
    failures = check()
    if failures:
        raise SystemExit("\n".join(failures))
    config = yaml.safe_load(args.config.read_text())
    endpoint_path = args.endpoints or Path(config["longitudinal_endpoints_local"])
    if not endpoint_path.exists():
        raise SystemExit(f"controlled local longitudinal endpoint table is unavailable: {endpoint_path}")
    endpoint = pd.read_csv(endpoint_path, dtype={"session": str})
    spatial = [name for name in ("gait_speed", "step_length_mean", "stride_length_mean") if name in endpoint]
    endpoint.loc[:, spatial] = endpoint.loc[:, spatial].apply(pd.to_numeric, errors="coerce") / 100.0
    frozen = load_frozen_model(args.model)
    bootstrap, participant = reference_bootstrap(
        _controls(args.v1_root),
        endpoint,
        frozen["features"],
        iterations=int(config["control_reference_bootstrap_iterations"]),
        seed=int(config["seed"]),
        covariance_method=config["covariance_method"],
    )
    summary = summarize_reference_uncertainty(bootstrap)
    args.output.mkdir(parents=True, exist_ok=True)
    bootstrap.to_csv(args.output / "reference_bootstrap_longitudinal.csv", index=False)
    summary.to_csv(args.output / "reference_uncertainty_summary.csv", index=False)
    participant.to_csv(args.output / "reference_uncertainty_participant_local.csv", index=False)
    _update_summary(args.output / "v4_6_summary.json", summary)


if __name__ == "__main__":
    main()
