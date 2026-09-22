#!/usr/bin/env python3
"""Aggregate-only correction of the v4.4 nonlinear session endpoint."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import bootstrap

from scripts.run_v4_3_v1_equivalence import icc_a1
from src.v4_1.normative import load_frozen_model, score
from src.v4_3.walkway_reconstruction import FEATURES
from src.v4_4.measurement_protocol import median_pass_endpoint
from src.v4_2.repeated_group_cv import favorable_fraction


def endpoint_resampling(passes: pd.DataFrame, model: dict, seed: int, draws: int = 2000) -> float:
    """Conditional technical SD of median(features) -> frozen score."""
    if len(passes) != 4:
        raise ValueError("exactly four passes required")
    rng = np.random.default_rng(seed)
    sampled = passes.loc[:, FEATURES].to_numpy(float)[rng.integers(0, 4, size=(draws, 4))]
    table = pd.DataFrame(np.median(sampled, axis=1), columns=FEATURES)
    table[["gait_speed", "step_length_mean", "stride_length_mean"]] /= 100
    table["age"] = float(passes.age.iloc[0])
    table["height_m"] = float(passes.height_m.iloc[0])
    return float(score(table, model).std(ddof=1))


def analyze(passes: pd.DataFrame, endpoints: pd.DataFrame, model: dict) -> pd.DataFrame:
    if endpoints.duplicated(["participant", "session", "task"]).any():
        raise ValueError("duplicate participant/session/task endpoint")
    if passes.duplicated(["participant", "session", "task", "pass"]).any():
        raise ValueError("duplicate participant/session/task/pass")
    precision = []
    for index, (_, group) in enumerate(passes.groupby(["participant", "session", "task"], sort=True)):
        if len(group) != 4:
            raise ValueError("incomplete pass group")
        stored = endpoints.loc[(endpoints.participant == group.participant.iloc[0]) &
                               (endpoints.session.astype(str) == str(group.session.iloc[0])) &
                               (endpoints.task == group.task.iloc[0])]
        if len(stored) != 1:
            raise ValueError("missing or duplicate session endpoint")
        candidate = median_pass_endpoint(group, 4).to_frame().T
        candidate[["gait_speed", "step_length_mean", "stride_length_mean"]] /= 100
        candidate["age"], candidate["height_m"] = group.age.iloc[0], group.height_m.iloc[0]
        if not np.isclose(score(candidate, model).iloc[0], stored.score.iloc[0], atol=1e-9):
            raise ValueError("stored endpoint does not equal median-to-score transformation")
        precision.append((*group[["participant", "session", "task"]].iloc[0],
                          endpoint_resampling(group, model, 20260924 + index)))
    technical = pd.DataFrame(precision, columns=["participant", "session", "task", "technical_sd"])
    records = []
    for task, group in endpoints.groupby("task", sort=True):
        paired = group.pivot(index="participant", columns="session", values="score").dropna()
        change = (paired["2"] - paired["1"]).to_numpy(float)
        rng = np.random.default_rng(20260924)
        boot = change[rng.integers(0, len(change), size=(2000, len(change)))]
        dispersion = np.std(change, ddof=1)
        bca = bootstrap((paired["1"].to_numpy(float), paired["2"].to_numpy(float)),
                        lambda first, second: icc_a1(first, second), paired=True,
                        n_resamples=2000, method="BCa", random_state=20260924).confidence_interval
        technical_sd = technical.loc[technical.task.eq(task) & technical.participant.isin(paired.index), "technical_sd"].to_numpy(float)
        records.append({
            "task": task, "n_paired": len(change), "estimand": "six_plus_month_longitudinal_stability",
            "icc_bca_ci_low": float(bca.low), "icc_bca_ci_high": float(bca.high),
            "longitudinal_stability_status": "FAIL", "short_term_reliability_status": "NOT_ESTIMABLE",
            "mean_change": float(change.mean()), "mean_change_ci_low": float(np.quantile(boot.mean(axis=1), .025)),
            "mean_change_ci_high": float(np.quantile(boot.mean(axis=1), .975)),
            "session_difference_sd": float(dispersion),
            "longitudinal_sem_equivalent": float(dispersion / np.sqrt(2)),
            "longitudinal_mdc95_equivalent": float(1.96 * dispersion),
            "conditional_pass_resampling_sd_median": float(np.median(technical_sd)),
            "pass_resampling_note": "Technical precision conditional on four observed passes; no biological state control",
        })
    return pd.DataFrame(records)


def describe_instability(passes: pd.DataFrame, endpoints: pd.DataFrame) -> pd.DataFrame:
    """Observed spread at each design level; these are not causal variance components."""
    rows = []
    for task, group in endpoints.groupby("task", sort=True):
        paired = group.pivot(index="participant", columns="session", values="score").dropna()
        kept = passes.loc[passes.task.eq(task) & passes.participant.isin(paired.index)]
        pass_variances = kept.groupby(["participant", "session"]).score.var(ddof=1)
        rows.append({"task": task, "n_paired": len(paired),
                     "between_person_endpoint_sd": float(paired.mean(axis=1).std(ddof=1)),
                     "between_visit_endpoint_difference_sd": float((paired["2"]-paired["1"]).std(ddof=1)),
                     "within_session_pass_score_sd": float(np.sqrt(pass_variances.mean())),
                     "state_variance_status": "NOT_ESTIMABLE_NO_SESSION_MEDICATION_ANCHOR"})
    both = endpoints.pivot(index=["participant", "session"], columns="task", values="score").dropna()
    contrast = both["HurriedPace"]-both["SelfPace"]
    for row in rows:
        row.update(n_paired_task_sessions=int(len(contrast)),
                   hurried_minus_self_mean=float(contrast.mean()),
                   hurried_minus_self_sd=float(contrast.std(ddof=1)))
    return pd.DataFrame(rows)


def selection_summary(endpoints: pd.DataFrame, exclusions: pd.DataFrame, v1_root: Path) -> pd.DataFrame:
    clinical = pd.read_csv(v1_root / "PD - Demographic+Clinical - datasetV1.csv", header=1)
    clinical = clinical.rename(columns={"Subject ID": "participant", "Age (years)": "age", "MDSUPDRS_3-10": "gait_item"})
    clinical["participant"] = clinical.participant.astype(str).str.strip()
    if clinical.duplicated("participant").any():
        raise ValueError("V1 clinical participant identifiers are not unique")
    clinical = clinical.set_index("participant")
    rows = []
    for task, group in endpoints.groupby("task", sort=True):
        paired = group.pivot(index="participant", columns="session", values="score").dropna()
        missing = set(exclusions.loc[exclusions.task.eq(task), "participant"])
        for label, people in (("complete_pair", set(paired.index)), ("excluded_four_pass", missing)):
            matched = clinical.reindex(sorted(people))
            gait = pd.to_numeric(matched.gait_item, errors="coerce")
            age = pd.to_numeric(matched.age, errors="coerce")
            rows.append({"task": task, "group": label, "n_participants": len(people),
                         "n_v1_gait_item": int(gait.notna().sum()),
                         "v1_gait_item_median": float(gait.median()) if gait.notna().any() else np.nan,
                         "v1_age_mean": float(age.mean()) if age.notna().any() else np.nan,
                         "interpretation": "Descriptive identifier overlap only; V1 assessment date is not verified as longitudinal session 1"})
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("results/v4_4"))
    parser.add_argument("--output", type=Path, default=Path("results/v4_5"))
    parser.add_argument("--v1-root", required=True, type=Path)
    args = parser.parse_args()
    model = load_frozen_model("results/v4_1/frozen/v4_1_control_model.json")
    passes = pd.read_csv(args.input / "h4b_pass_scores_local.csv", dtype={"session": str})
    endpoints = pd.read_csv(args.input / "h4b_session_endpoints_local.csv", dtype={"session": str})
    args.output.mkdir(parents=True, exist_ok=True)
    analyze(passes, endpoints, model).to_csv(args.output / "h4b_endpoint_error_corrected.csv", index=False)
    describe_instability(passes, endpoints).to_csv(args.output / "instability_descriptive.csv", index=False)
    exclusions = pd.read_csv(args.input / "h4b_multipass_exclusions.csv")
    selection_summary(endpoints, exclusions, args.v1_root).to_csv(args.output / "complete_case_selection.csv", index=False)
    runs = pd.read_csv("results/v4_2/frozen/h2_repeated_cv_runs.csv")
    summary = []
    for level, group in runs.groupby("level"):
        summary.append({"level": level, **{f"delta_{metric}_favorable_fraction": favorable_fraction(group, metric)
                                           for metric in ("mae", "rmse", "spearman_rho", "pearson_r", "calibration_slope", "calibration_intercept")}})
    pd.DataFrame(summary).to_csv(args.output / "h2_favorable_fraction_corrected.csv", index=False)
    def digest(path: Path) -> str:
        value = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                value.update(chunk)
        return value.hexdigest()
    (args.output / "method.json").write_text(json.dumps({"model_sha256": "b3d04cc17a08de4c213abe3d01f7d378b161a75df847da8022659c11312dfb53",
        "source": "v4.4 local reconstructed passes and endpoints",
        "input_sha256": {name: digest(args.input / name) for name in ("h4b_pass_scores_local.csv", "h4b_session_endpoints_local.csv")},
        "seed": 20260924, "pass_resamples_per_session": 2000,
        "endpoint": "frozen score(featurewise median of four passes)",
        "longitudinal_error_caveat": "Six-plus-month paired change includes progression and state effects; SEM/MDC equivalents are not pure measurement error"}, indent=2) + "\n")


if __name__ == "__main__":
    main()
