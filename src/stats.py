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
    covariates = ("gait_speed", "age", "height_m", "task", "site", "sex", "dbs_status", "medication_state", "time_since_medication", "disease_duration")
    columns = [severity] + [c for c in covariates if c in frame and c != severity]
    categorical = [c for c in columns if not pd.api.types.is_numeric_dtype(frame[c])]
    x = pd.get_dummies(frame[columns], columns=categorical, drop_first=True, dtype=float)
    return np.c_[np.ones(len(x)), x.to_numpy(float)], ["intercept"] + list(x.columns)


def adjusted_associations(table: pd.DataFrame, features: list[str], severity: str) -> pd.DataFrame:
    """OLS feature associations with fixed context covariates and 95% CIs.

    This intentionally reports association only; it is not a mixed-effects
    replacement when repeated measurements are sufficiently large.
    """
    rows = []
    for feature in features:
        covariates = ("gait_speed", "age", "height_m", "task", "site", "sex", "dbs_status", "medication_state", "time_since_medication", "disease_duration")
        keep = [feature, severity] + [c for c in covariates if c in table and c != feature and c != severity]
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


def variance_decomposition(table: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    """Descriptive variance fractions by participant, site, task and session.

    This is an ANOVA-style decomposition, not a claim of mixed-model variance
    components. Fractions are calculated from nested group means and residuals.
    """
    rows = []
    for feature in features:
        cols = [feature] + [c for c in ("participant_id", "site", "task", "session_id") if c in table]
        frame = table[cols].dropna(subset=[feature])
        if len(frame) < 2:
            rows.append({"feature": feature, "n": len(frame), "total_variance": np.nan})
            continue
        y, mean = frame[feature].to_numpy(float), frame[feature].mean()
        total = float(np.sum((y - mean) ** 2))
        row = {"feature": feature, "n": len(frame), "total_variance": float(np.var(y, ddof=1))}
        for key in ("participant_id", "site", "task", "session_id"):
            if key in frame and frame[key].nunique(dropna=False) > 1:
                means = frame.groupby(key, dropna=False)[feature].transform("mean")
                row[f"{key}_fraction"] = float(np.sum((means - mean) ** 2) / total) if total else np.nan
            else:
                row[f"{key}_fraction"] = np.nan
        residual = y - frame.groupby([c for c in ("participant_id", "site", "task", "session_id") if c in frame], dropna=False)[feature].transform("mean").to_numpy()
        row["residual_fraction"] = float(np.sum(residual ** 2) / total) if total else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def reliability_icc(table: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    """Estimate repeatability with one-way random-effects ICC(1,1)."""
    rows = []
    for feature in features:
        if "participant_id" not in table or "session_id" not in table:
            rows.append({"feature": feature, "n": 0, "icc": np.nan})
            continue
        frame = table[["participant_id", "session_id", feature]].dropna()
        counts = frame.groupby("participant_id")["session_id"].nunique()
        frame = frame[frame.participant_id.isin(counts[counts > 1].index)]
        n, k = frame.participant_id.nunique(), frame.groupby("participant_id").size().mean() if not frame.empty else 0
        if n < 2 or k < 2:
            rows.append({"feature": feature, "n": len(frame), "icc": np.nan})
            continue
        means = frame.groupby("participant_id")[feature].mean()
        ms_between = len(frame.groupby("participant_id")) / (n - 1) * ((means - frame[feature].mean()) ** 2).sum()
        ms_within = ((frame.set_index("participant_id")[feature] - means) ** 2).sum() / (len(frame) - n)
        rows.append({"feature": feature, "n": len(frame), "icc": float((ms_between - ms_within) / (ms_between + (k - 1) * ms_within)) if ms_between + (k - 1) * ms_within else np.nan})
    return pd.DataFrame(rows)


def within_person_changes(table: pd.DataFrame, features: list[str], severity: str) -> pd.DataFrame:
    """Correlate within-person feature and severity changes when sessions repeat."""
    rows = []
    if "participant_id" not in table or "session_id" not in table or severity not in table:
        return pd.DataFrame(columns=["feature", "n_participants", "correlation"])
    for feature in features:
        frame = table[["participant_id", "session_id", feature, severity]].dropna()
        if frame.empty:
            rows.append({"feature": feature, "n_participants": 0, "correlation": np.nan}); continue
        delta = frame.groupby("participant_id")[[feature, severity]].agg(lambda x: x.iloc[-1] - x.iloc[0])
        rows.append({"feature": feature, "n_participants": len(delta), "correlation": delta[feature].corr(delta[severity]) if len(delta) >= 3 else np.nan})
    return pd.DataFrame(rows)
