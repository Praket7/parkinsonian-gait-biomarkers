"""Participant-aware statistical helpers for analysis v3.

Every routine returns an explicit status; unavailable data are never silently
converted into a failed scientific criterion.
"""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
try:
    import statsmodels.api as sm
except ImportError:  # ICC/QC helpers remain testable without the analysis extra.
    sm = None
from scipy.stats import spearmanr

from .stats import bh_fdr


PASS, FAIL, NOT_ESTIMABLE = "PASS", "FAIL", "NOT_ESTIMABLE"


def z(values):
    values = pd.to_numeric(values, errors="coerce")
    scale = values.std(ddof=0)
    return (values - values.mean()) / scale if np.isfinite(scale) and scale else values * np.nan


def _fit(frame, formula):
    if sm is None:
        raise ValueError("statsmodels is required for GEE inference")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return sm.GEE.from_formula(formula, groups="participant_id", data=frame,
                                   cov_struct=sm.cov_struct.Exchangeable(),
                                   family=sm.families.Gaussian()).fit()


def _ready(table, feature, *, include_speed=False, task_interaction=False, site_interaction=False, minimum_participants=20):
    columns = [feature, "mds_updrs_gait_item", "age", "height_m", "sex", "task", "site", "participant_id"]
    if include_speed and feature != "gait_speed":
        columns.append("gait_speed")
    frame = table[columns].dropna().copy()
    if len(frame) < 30 or frame.participant_id.nunique() < minimum_participants or frame[feature].nunique() < 4:
        return frame, None
    if task_interaction and frame.task.nunique() < 2:
        return frame, None
    if site_interaction and frame.site.nunique() < 2:
        return frame, None
    frame["outcome_z"] = z(frame[feature])
    frame["severity_z"] = z(frame.mds_updrs_gait_item)
    frame["age_z"] = z(frame.age)
    frame["height_z"] = z(frame.height_m)
    if include_speed and feature != "gait_speed":
        frame["gait_speed_z"] = z(frame.gait_speed)
    return frame, frame.outcome_z.notna().all() and frame.severity_z.notna().all()


def gee_association(table, feature, *, speed_adjusted=False, task_interaction=False,
                    site_interaction=False, minimum_participants=20):
    """Fit the declared GEE and return the severity trend plus robust status."""
    frame, usable = _ready(table, feature, include_speed=speed_adjusted,
                           task_interaction=task_interaction, site_interaction=site_interaction,
                           minimum_participants=minimum_participants)
    row = {"feature": feature, "n_rows": len(frame), "n_participants": frame.participant_id.nunique(),
           "effect": np.nan, "ci_low": np.nan, "ci_high": np.nan, "p_value": np.nan,
           "status": NOT_ESTIMABLE}
    if not usable:
        return row
    rhs = "severity_z + age_z + height_z + C(sex) + C(task) + C(site)"
    if speed_adjusted and feature != "gait_speed":
        rhs += " + gait_speed_z"
    if task_interaction:
        rhs += " + severity_z:C(task)"
    if site_interaction:
        rhs += " + severity_z:C(site)"
    try:
        fit = _fit(frame, f"outcome_z ~ {rhs}")
        interval = fit.conf_int().loc["severity_z"]
        row.update(effect=float(fit.params["severity_z"]), ci_low=float(interval.iloc[0]),
                   ci_high=float(interval.iloc[1]), p_value=float(fit.pvalues["severity_z"]), status="OK")
        terms = [name for name in fit.params.index if name.startswith("severity_z:C(")]
        if terms:
            indexes = [fit.params.index.get_loc(name) for name in terms]
            constraint = np.zeros((len(indexes), len(fit.params)))
            constraint[np.arange(len(indexes)), indexes] = 1
            row["interaction_p_value"] = float(np.asarray(fit.wald_test(constraint, scalar=False).pvalue).squeeze())
        return row
    except (ValueError, np.linalg.LinAlgError, KeyError):
        row["status"] = "FIT_FAILED"
        return row


def association_table(table, features, config):
    """Primary, speed-adjusted, interaction, and ordinal/rank sensitivities."""
    minimum = config["minimum_model_participants"]
    primary = [gee_association(table, feature, minimum_participants=minimum) for feature in features]
    speed = [gee_association(table, feature, speed_adjusted=True, minimum_participants=minimum) for feature in features]
    task = [gee_association(table, feature, task_interaction=True, minimum_participants=minimum) for feature in features]
    site = [gee_association(table, feature, site_interaction=True, minimum_participants=minimum) for feature in features]
    result = pd.DataFrame(primary).set_index("feature")
    result["q_value"] = bh_fdr(result.p_value)
    for label, rows in (("speed_adjusted", speed), ("task_interaction", task), ("site_interaction", site)):
        addon = pd.DataFrame(rows).set_index("feature")
        for column in ("effect", "ci_low", "ci_high", "p_value", "status", "interaction_p_value"):
            if column in addon:
                result[f"{label}_{column}"] = addon[column]
    result["speed_adjusted_q_value"] = bh_fdr(result.speed_adjusted_p_value)
    for feature in features:
        frame, usable = _ready(table, feature, minimum_participants=minimum)
        if usable:
            result.loc[feature, "rank_spearman_rho"] = spearmanr(frame[feature], frame.mds_updrs_gait_item).statistic
            # Categorical-score GEE is an ordinal-target sensitivity without
            # pretending the 0--4 spacing is inherently interval-scaled.
            try:
                fit = _fit(frame, "outcome_z ~ C(mds_updrs_gait_item) + age_z + height_z + C(sex) + C(task) + C(site)")
                names = [n for n in fit.params.index if n.startswith("C(mds_updrs_gait_item)")]
                idx = [fit.params.index.get_loc(n) for n in names]
                constraint = np.zeros((len(idx), len(fit.params))); constraint[np.arange(len(idx)), idx] = 1
                result.loc[feature, "severity_categorical_p_value"] = float(np.asarray(fit.wald_test(constraint, scalar=False).pvalue).squeeze())
            except (ValueError, np.linalg.LinAlgError, KeyError):
                result.loc[feature, "severity_categorical_p_value"] = np.nan
    return result.reset_index()


def gee_bootstrap(table, associations, config):
    """Refit the primary GEE on whole-participant bootstrap samples."""
    rng, iterations = np.random.default_rng(config["seed"]), int(config["bootstrap_iterations"])
    output = []
    for association in associations.itertuples(index=False):
        feature = association.feature
        primary = association.effect
        frame, usable = _ready(table, feature, minimum_participants=config["minimum_model_participants"])
        if not usable or not np.isfinite(primary):
            output.append({"feature": feature, "bootstrap_status": NOT_ESTIMABLE}); continue
        people = frame.participant_id.unique(); effects = []
        for _ in range(iterations):
            chosen = rng.choice(people, len(people), replace=True)
            sample = pd.concat([frame[frame.participant_id.eq(person)].assign(participant_id=f"boot_{i}") for i, person in enumerate(chosen)], ignore_index=True)
            try:
                effects.append(float(_fit(sample, "outcome_z ~ severity_z + age_z + height_z + C(sex) + C(task) + C(site)").params["severity_z"]))
            except (ValueError, np.linalg.LinAlgError, KeyError):
                continue
        values = np.asarray(effects)
        output.append({"feature": feature, "bootstrap_status": "OK" if len(values) >= iterations * .9 else "FIT_INCOMPLETE",
                       "bootstrap_n": int(len(values)), "bootstrap_same_sign_fraction": float(np.mean(values * np.sign(primary) > 0)) if len(values) else np.nan,
                       "bootstrap_median": float(np.median(values)) if len(values) else np.nan,
                       "bootstrap_ci_low": float(np.quantile(values, .025)) if len(values) else np.nan,
                       "bootstrap_ci_high": float(np.quantile(values, .975)) if len(values) else np.nan})
    return pd.DataFrame(output)


def task_specific_and_leave_site_out(table, features, config):
    rows, minimum = [], config["minimum_model_participants"]
    for feature in features:
        primary = gee_association(table, feature, minimum_participants=minimum)
        for task in sorted(table.task.dropna().unique()):
            subset = table[table.task.eq(task)]
            item = gee_association(subset, feature, minimum_participants=max(8, minimum // 2))
            rows.append({"feature": feature, "analysis": "task_specific", "level": task, **item})
        for site in sorted(table.site.dropna().unique()):
            subset = table[~table.site.eq(site)]
            item = gee_association(subset, feature, minimum_participants=max(8, minimum // 2))
            same = np.sign(item["effect"]) == np.sign(primary["effect"]) if np.isfinite(item["effect"]) and np.isfinite(primary["effect"]) else np.nan
            rows.append({"feature": feature, "analysis": "leave_one_site_out", "level": site, "same_direction": same, **item})
    return pd.DataFrame(rows)


def participant_permutations(table, features, config):
    """Empirical p values after participant-level severity-label shuffling."""
    rng, iterations, minimum = np.random.default_rng(config["seed"] + 1), int(config["permutation_iterations"]), config["minimum_model_participants"]
    rows = []
    for feature in features:
        observed = gee_association(table, feature, minimum_participants=minimum)
        frame, usable = _ready(table, feature, minimum_participants=minimum)
        if not usable or not np.isfinite(observed["effect"]):
            rows.append({"feature": feature, "permutation_status": NOT_ESTIMABLE}); continue
        participant_scores = frame.groupby("participant_id").mds_updrs_gait_item.first()
        estimates = []
        for _ in range(iterations):
            shuffled = participant_scores.copy(); shuffled[:] = rng.permutation(shuffled.to_numpy())
            sample = frame.copy(); sample["severity_z"] = sample.participant_id.map(shuffled).pipe(z)
            try:
                estimates.append(float(_fit(sample, "outcome_z ~ severity_z + age_z + height_z + C(sex) + C(task) + C(site)").params["severity_z"]))
            except (ValueError, np.linalg.LinAlgError, KeyError):
                pass
        values = np.asarray(estimates)
        rows.append({"feature": feature, "permutation_status": "OK" if len(values) >= iterations * .9 else "FIT_INCOMPLETE",
                     "permutation_n": int(len(values)), "permutation_p_value": float((1 + np.sum(np.abs(values) >= abs(observed["effect"]))) / (1 + len(values))) if len(values) else np.nan})
    return pd.DataFrame(rows)


def medication_sensitivity(table, features, config):
    """Adjust the primary GEE for recorded state, or dosing interval if usable."""
    rows = []
    candidates = ("medication_state", "time_since_medication")
    available = next((name for name in candidates if name in table and table[name].notna().sum() >= 20), None)
    for feature in features:
        base = {"feature": feature, "adjuster": available, "effect": np.nan, "p_value": np.nan,
                "status": NOT_ESTIMABLE}
        if not available:
            rows.append(base); continue
        columns = [feature, "mds_updrs_gait_item", "age", "height_m", "sex", "task", "site", "participant_id", available]
        frame = table[columns].dropna().copy()
        if frame.participant_id.nunique() < config["minimum_model_participants"] or frame[available].nunique() < 2:
            rows.append(base); continue
        frame["outcome_z"], frame["severity_z"], frame["age_z"], frame["height_z"] = z(frame[feature]), z(frame.mds_updrs_gait_item), z(frame.age), z(frame.height_m)
        rhs = "severity_z + age_z + height_z + C(sex) + C(task) + C(site)"
        rhs += f" + C({available})" if available == "medication_state" else f" + {available}"
        try:
            fit = _fit(frame, f"outcome_z ~ {rhs}")
            base.update(effect=float(fit.params["severity_z"]), p_value=float(fit.pvalues["severity_z"]), status="OK")
        except (ValueError, np.linalg.LinAlgError, KeyError):
            base["status"] = "FIT_FAILED"
        rows.append(base)
    return pd.DataFrame(rows)


def negative_controls(table, config):
    """Prespecified null checks using the same participant-clustered GEE."""
    columns = ["gait_speed", "mds_updrs_gait_item", "age", "height_m", "sex", "task", "site", "participant_id"]
    frame = table[columns].dropna().copy()
    if frame.participant_id.nunique() < config["minimum_model_participants"]:
        return pd.DataFrame([{"control": name, "status": NOT_ESTIMABLE} for name in ("gaussian_feature", "shuffled_severity", "site_only_severity")])
    frame["outcome_z"], frame["severity_z"], frame["age_z"], frame["height_z"] = z(frame.gait_speed), z(frame.mds_updrs_gait_item), z(frame.age), z(frame.height_m)
    rng = np.random.default_rng(config["seed"] + 3); rows = []
    scores = frame.groupby("participant_id", sort=False).mds_updrs_gait_item.first()
    shuffled = dict(zip(scores.index, rng.permutation(scores.to_numpy())))
    for name, sample, formula, term in (
        ("gaussian_feature", frame.assign(outcome_z=rng.normal(size=len(frame))), "outcome_z ~ severity_z + age_z + height_z + C(sex) + C(task) + C(site)", "severity_z"),
        ("shuffled_severity", frame.assign(severity_z=frame.participant_id.map(shuffled).pipe(z)), "outcome_z ~ severity_z + age_z + height_z + C(sex) + C(task) + C(site)", "severity_z"),
        ("site_only_severity", frame, "severity_z ~ C(site)", None),
    ):
        try:
            fit = _fit(sample, formula)
            if term:
                rows.append({"control": name, "effect": float(fit.params[term]), "p_value": float(fit.pvalues[term]), "status": "OK"})
            else:
                names = [n for n in fit.params.index if n.startswith("C(site)")]
                idx = [fit.params.index.get_loc(n) for n in names]; constraint = np.zeros((len(idx), len(fit.params))); constraint[np.arange(len(idx)), idx] = 1
                rows.append({"control": name, "effect": np.nan, "p_value": float(np.asarray(fit.wald_test(constraint, scalar=False).pvalue).squeeze()), "status": "OK"})
        except (ValueError, np.linalg.LinAlgError, KeyError):
            rows.append({"control": name, "effect": np.nan, "p_value": np.nan, "status": "FIT_FAILED"})
    return pd.DataFrame(rows)


def icc_2_1(values):
    """Exact two-way random, absolute-agreement, single-measure ICC(A,1)."""
    values = np.asarray(values, dtype=float)
    if values.ndim != 2 or values.shape[0] < 2 or values.shape[1] < 2 or not np.isfinite(values).all():
        return np.nan, np.nan
    n, k = values.shape; grand = values.mean(); row = values.mean(1); column = values.mean(0)
    msr = k * np.sum((row - grand) ** 2) / (n - 1)
    msc = n * np.sum((column - grand) ** 2) / (k - 1)
    mse = np.sum((values - row[:, None] - column + grand) ** 2) / ((n - 1) * (k - 1))
    denominator = msr + (k - 1) * mse + k * (msc - mse) / n
    return float((msr - mse) / denominator) if denominator else np.nan, float(mse)


def reliability_by_task(table, features, config):
    rng, rows = np.random.default_rng(config["seed"] + 2), []
    for feature in features:
        for task in sorted(table.task.dropna().unique()):
            frame = table.loc[table.task.eq(task), ["participant_id", "session_id", feature]].dropna()
            wide = frame.pivot_table(index="participant_id", columns="session_id", values=feature, aggfunc="mean").dropna()
            if len(wide) < config["reliability"]["minimum_participants"] or wide.shape[1] < 2:
                rows.append({"feature": feature, "task": task, "n_participants": len(wide), "icc_model": "ICC(A,1)", "status": NOT_ESTIMABLE}); continue
            values = wide.iloc[:, :2].to_numpy(float); estimate, mse = icc_2_1(values)
            boot = []
            for _ in range(config["reliability"]["bootstrap_iterations"]):
                index = rng.integers(0, len(values), len(values)); value, _ = icc_2_1(values[index])
                if np.isfinite(value): boot.append(value)
            rows.append({"feature": feature, "task": task, "n_participants": len(wide), "icc_model": "ICC(A,1)", "icc_2_1": estimate,
                         "icc_ci_low": float(np.quantile(boot, .025)) if boot else np.nan, "icc_ci_high": float(np.quantile(boot, .975)) if boot else np.nan,
                         "sem": float(np.sqrt(mse)), "mdc95": float(1.96 * np.sqrt(2 * mse)), "status": "OK"})
    return pd.DataFrame(rows)
