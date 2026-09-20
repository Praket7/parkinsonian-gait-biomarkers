"""Small, deterministic inferential helpers for the frozen feature table."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import t


def bh_fdr(p_values: pd.Series) -> pd.Series:
    """Benjamini-Hochberg adjusted values, preserving missing tests."""
    out = pd.Series(np.nan, index=p_values.index, dtype=float)
    valid = p_values.dropna()
    if valid.empty:
        return out
    order = valid.sort_values().index
    adjusted = valid.loc[order].to_numpy() * len(valid) / np.arange(1, len(valid) + 1)
    out.loc[order] = np.minimum.accumulate(adjusted[::-1])[::-1].clip(0, 1)
    return out


def _design(frame: pd.DataFrame, severity: str) -> tuple[np.ndarray, list[str]]:
    columns = [severity] + [c for c in ("gait_speed", "age", "height_m", "task", "site", "sex", "dbs_status") if c in frame]
    x = pd.get_dummies(frame[columns], columns=[c for c in columns if frame[c].dtype == object], drop_first=True, dtype=float)
    return np.c_[np.ones(len(x)), x.to_numpy(float)], ["intercept"] + list(x.columns)


def adjusted_associations(table: pd.DataFrame, features: list[str], severity: str) -> pd.DataFrame:
    """OLS feature associations with fixed context covariates and 95% CIs.

    This intentionally reports association only; it is not a mixed-effects
    replacement when repeated measurements are sufficiently large.
    """
    rows = []
    for feature in features:
        keep = [feature, severity] + [c for c in ("gait_speed", "age", "height_m", "task", "site", "sex", "dbs_status") if c in table]
        frame = table[keep].dropna()
        if len(frame) < 12 or frame[severity].nunique() < 3:
            rows.append({"feature": feature, "n": len(frame), "effect": np.nan, "ci_low": np.nan, "ci_high": np.nan, "p_value": np.nan})
            continue
        x, names = _design(frame, severity)
        y = frame[feature].to_numpy(float)
        beta, _, rank, _ = np.linalg.lstsq(x, y, rcond=None)
        df = len(y) - rank
        if df <= 0 or severity not in names:
            rows.append({"feature": feature, "n": len(frame), "effect": np.nan, "ci_low": np.nan, "ci_high": np.nan, "p_value": np.nan})
            continue
        residual = y - x @ beta
        covariance = np.linalg.pinv(x.T @ x) * (residual @ residual / df)
        index = names.index(severity)
        se = np.sqrt(covariance[index, index])
        statistic = beta[index] / se if se else np.nan
        critical = t.ppf(0.975, df)
        rows.append({"feature": feature, "n": len(frame), "effect": beta[index], "ci_low": beta[index] - critical * se, "ci_high": beta[index] + critical * se, "p_value": 2 * t.sf(abs(statistic), df)})
    result = pd.DataFrame(rows)
    result["q_value"] = bh_fdr(result["p_value"])
    return result


def participant_bootstrap_direction(table: pd.DataFrame, features: list[str], severity: str, iterations: int, seed: int) -> pd.Series:
    """Resample participant clusters, never individual walks."""
    if "participant_id" not in table or table["participant_id"].nunique() < 3:
        return pd.Series(np.nan, index=features, name="direction_consistency")
    rng, people = np.random.default_rng(seed), table["participant_id"].dropna().unique()
    signs = {feature: [] for feature in features}
    for _ in range(iterations):
        sampled = rng.choice(people, size=len(people), replace=True)
        boot = pd.concat([table[table.participant_id == person].assign(_bootstrap_person=i) for i, person in enumerate(sampled)], ignore_index=True)
        estimates = adjusted_associations(boot, features, severity).set_index("feature")["effect"]
        for feature, value in estimates.items():
            if np.isfinite(value):
                signs[feature].append(np.sign(value))
    return pd.Series({feature: np.mean(np.asarray(values) == np.sign(np.nanmean(values))) if values else np.nan for feature, values in signs.items()}, name="direction_consistency")
