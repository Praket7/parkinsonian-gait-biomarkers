#!/usr/bin/env python3
"""Run the frozen-model, four-pass median protocol extension (v4.4)."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from run_v4_3_h4_longitudinal import bootstrap_icc, clinical_covariates
from run_v4_3_v1_equivalence import icc_a1
from src.v4_1.normative import score
from src.v4_3.walkway_reconstruction import FEATURES, reconstruct_passes_csv
from src.v4_4.measurement_protocol import median_pass_endpoint, variance_components


def _model(path: Path) -> dict:
    model = json.loads(path.read_text())
    model["features"] = model.pop("feature_order")
    model["beta"] = np.asarray(model["beta"])
    model["covariance"] = np.asarray(model["covariance"])
    return model


def _files(root: Path):
    expression = re.compile(r"(?P<participant>.+?)s(?P<session>[12])_(?P<task>SelfPace|HurriedPace)$")
    for path in sorted((root / "PD Participants" / "00-CSV files").glob("*s[12]_*.csv")):
        match = expression.fullmatch(path.stem)
        if match:
            yield path, match.groupdict()


def _score(table: pd.DataFrame, model: dict) -> pd.Series:
    metric_columns = ["gait_speed", "step_length_mean", "stride_length_mean"]
    converted = table.copy()
    converted.loc[:, metric_columns] = converted.loc[:, metric_columns] / 100.0
    return score(converted, model)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v1-root", required=True, type=Path)
    parser.add_argument("--longitudinal-root", required=True, type=Path)
    parser.add_argument("--model", default="results/v4_1/frozen/v4_1_control_model.json", type=Path)
    parser.add_argument("--v1-qc", default="results/v4_3/v1_reconstruction_qc.json", type=Path)
    parser.add_argument("--config", default="configs/v4_4_analysis.yaml", type=Path)
    parser.add_argument("--output", default="results/v4_4", type=Path)
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text())
    if not json.loads(args.v1_qc.read_text())["all_eight_equivalent"]:
        raise SystemExit("v4.3 analytical-equivalence bridge is required")
    rows, exclusions = [], []
    for path, key in _files(args.longitudinal_root):
        try:
            passes = reconstruct_passes_csv(str(path))
            endpoint = median_pass_endpoint(passes, config["required_valid_passes_per_session"])
            passes = passes.assign(**key, source_file=str(path))
            rows.extend(passes.to_dict("records"))
            rows.append({**key, "source_file": str(path), "pass": "median_4pass", **endpoint.to_dict()})
        except (ValueError, pd.errors.ParserError) as error:
            exclusions.append({**key, "source_file": str(path), "reason": str(error)})
    all_rows = pd.DataFrame(rows)
    raw_passes = all_rows[all_rows["pass"].astype(str).ne("median_4pass")].copy()
    endpoints = all_rows[all_rows["pass"].astype(str).eq("median_4pass")].copy()
    covariates = clinical_covariates(args.v1_root)
    model = _model(args.model)
    raw_passes = raw_passes.merge(covariates, on="participant", how="inner")
    endpoints = endpoints.merge(covariates, on="participant", how="inner")
    raw_passes["score"] = _score(raw_passes, model)
    endpoints["score"] = _score(endpoints, model)
    records = []
    for task, group in endpoints.groupby("task", sort=True):
        paired = group.pivot_table(index="participant", columns="session", values="score", aggfunc="first").dropna()
        lower, upper = bootstrap_icc(paired["1"].to_numpy(), paired["2"].to_numpy(), seed=config["seed"], n=config["bootstrap_iterations"])
        components = variance_components(raw_passes[raw_passes.task.eq(task) & raw_passes.participant.isin(paired.index)])
        records.append({"task": task, "endpoint": config["endpoint_name"], "aggregation": config["aggregation"],
                        "estimability_status": "OK", "n_participants": len(paired), "icc_a1": icc_a1(paired["1"].to_numpy(), paired["2"].to_numpy()),
                        "icc_a1_ci_low": lower, "icc_a1_ci_high": upper,
                        "mean_change_s2_minus_s1": float((paired["2"] - paired["1"]).mean()),
                        "mae": float((paired["2"] - paired["1"]).abs().mean()),
                        "test_retest_status": "PASS" if lower >= config["reliability_lower_ci_threshold"] else "FAIL", **components})
    args.output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_csv(args.output / "h4b_multipass_reliability.csv", index=False)
    pd.DataFrame(exclusions).to_csv(args.output / "h4b_multipass_exclusions.csv", index=False)
    # Never publish row-level authorized data; this local audit is ignored by Git.
    raw_passes.to_csv(args.output / "h4b_pass_scores_local.csv", index=False)
    endpoints.to_csv(args.output / "h4b_session_endpoints_local.csv", index=False)
    (args.output / "h4b_protocol_qc.json").write_text(json.dumps({
        "protocol": config["analysis_version"], "parent_release": config["parent_release"], "model_refit": False,
        "v4_3_bridge": "PASS", "endpoint": config["endpoint_name"], "required_valid_passes_per_session": config["required_valid_passes_per_session"],
        "eligible_session_endpoints": int(len(endpoints)), "excluded_session_files": int(len(exclusions)),
        "clinical_responsiveness_status": config["clinical_responsiveness"]["status_if_missing"],
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
