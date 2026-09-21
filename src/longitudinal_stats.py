"""Small participant-aware longitudinal tools for external validation."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

try:
    import statsmodels.api as sm
except ImportError:  # pragma: no cover
    sm = None

OK, NOT_ESTIMABLE, FIT_FAILED = "OK", "NOT_ESTIMABLE", "FIT_FAILED"


def within_between_decomposition(table: pd.DataFrame, anchor: str, participant: str = "participant_key") -> pd.DataFrame:
    result = table.copy()
    value = pd.to_numeric(result[anchor], errors="coerce")
    result["anchor_between"] = value.groupby(result[participant]).transform("mean")
    result["anchor_within"] = value - result["anchor_between"]
    return result


def standardized_response_mean(change) -> float:
    values = pd.Series(change, dtype=float).dropna()
    return float(values.mean() / values.std(ddof=1)) if len(values) > 1 and values.std(ddof=1) else np.nan


def measurement_error(repeated: pd.DataFrame, feature: str, participant: str = "participant_key") -> dict:
    pairs = repeated.pivot_table(index=participant, columns="visit_order", values=feature, aggfunc="mean").dropna()
    if pairs.shape[0] < 5 or pairs.shape[1] < 2:
        return {"feature": feature, "status": NOT_ESTIMABLE, "n_participants": int(pairs.shape[0])}
    values = pairs.iloc[:, :2].to_numpy(float)
    error = np.sum((values - values.mean(1, keepdims=True)) ** 2) / len(values)
    sem = float(np.sqrt(error))
    changes = np.abs(values[:, 1] - values[:, 0])
    mdc = float(1.96 * np.sqrt(2) * sem)
    return {"feature": feature, "status": OK, "n_participants": int(len(values)), "sem": sem, "mdc95": mdc,
            "median_abs_change": float(np.median(changes)), "mean_abs_change": float(np.mean(changes)),
            "proportion_exceeding_mdc95": float(np.mean(changes > mdc))}


def paired_change_summary(table: pd.DataFrame, feature: str, anchor: str, participant: str = "participant_key") -> dict:
    frame = table[[participant, "visit_order", feature, anchor]].dropna().sort_values([participant, "visit_order"])
    first_last = frame.groupby(participant, as_index=False).agg({feature: lambda x: x.iloc[-1] - x.iloc[0], anchor: lambda x: x.iloc[-1] - x.iloc[0]})
    if len(first_last) < 2:
        return {"feature": feature, "status": NOT_ESTIMABLE, "n_participants": int(len(first_last))}
    rho = spearmanr(first_last[feature], first_last[anchor]).statistic if len(first_last) > 2 else np.nan
    return {"feature": feature, "status": OK, "n_participants": int(len(first_last)), "mean_change": float(first_last[feature].mean()),
            "median_change": float(first_last[feature].median()), "srm": standardized_response_mean(first_last[feature]),
            "delta_anchor_spearman_rho": float(rho) if np.isfinite(rho) else np.nan}


def longitudinal_gee(table: pd.DataFrame, feature: str, anchor: str, participant: str = "participant_key") -> dict:
    columns = [participant, feature, anchor, "months_from_baseline"]
    frame = within_between_decomposition(table[columns].dropna(), anchor, participant)
    n_people = frame[participant].nunique()
    base = {"feature": feature, "anchor_used": anchor, "n_rows": len(frame), "n_participants": int(n_people), "status": NOT_ESTIMABLE}
    if sm is None or n_people < 20 or frame[feature].nunique() < 4 or frame.anchor_within.nunique() < 2:
        return base
    try:
        fit = sm.GEE.from_formula(f"{feature} ~ anchor_within + anchor_between + months_from_baseline", groups=participant,
                                  data=frame, family=sm.families.Gaussian(), cov_struct=sm.cov_struct.Exchangeable()).fit()
        ci = fit.conf_int().loc["anchor_within"]
        return {**base, "status": OK, "within_effect": float(fit.params.anchor_within), "ci_low": float(ci.iloc[0]),
                "ci_high": float(ci.iloc[1]), "p_value": float(fit.pvalues.anchor_within), "between_effect": float(fit.params.anchor_between)}
    except Exception:
        return {**base, "status": FIT_FAILED}
