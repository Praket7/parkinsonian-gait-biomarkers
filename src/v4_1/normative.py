"""Outcome-blind control-reference model used by the v4.1 validation."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf


FEATURES = ("gait_speed", "cadence", "step_length_mean", "stride_length_mean",
            "step_time_mean", "stride_time_mean", "step_time_cv", "stride_time_cv")
COVARIATES = ("age", "height_m")


def fit_reference(controls: pd.DataFrame, features=FEATURES, covariance_method="sample") -> dict:
    """Fit the declared reference using control observations only."""
    if controls.empty or controls.get("clinical_cohort", pd.Series(dtype=str)).astype(str).str.lower().eq("pd").any():
        raise ValueError("reference fitting accepts controls only")
    features = list(features)
    x = np.column_stack([np.ones(len(controls)), *[pd.to_numeric(controls[c], errors="coerce") for c in COVARIATES]])
    valid = np.isfinite(x).all(1) & controls[features].notna().all(1)
    x, y = x[valid], controls.loc[valid, features].to_numpy(float)
    if len(x) <= len(COVARIATES) + 2:
        raise ValueError("insufficient control observations")
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    residuals = y - x @ beta
    if covariance_method == "sample":
        covariance = np.cov(residuals, rowvar=False)
    elif covariance_method == "ledoit_wolf":
        covariance = LedoitWolf().fit(residuals).covariance_
    else:
        raise ValueError("unknown covariance method")
    return {"features": features, "covariates": list(COVARIATES), "beta": beta,
            "covariance": np.atleast_2d(covariance) + np.eye(len(features)) * 1e-6,
            "covariance_method": covariance_method}


def score(table: pd.DataFrame, model: dict) -> pd.Series:
    x = np.column_stack([np.ones(len(table)), *[pd.to_numeric(table[c], errors="coerce") for c in model["covariates"]]])
    residual = table[model["features"]].to_numpy(float) - x @ np.asarray(model["beta"])
    value = np.sqrt(np.einsum("ij,jk,ik->i", residual, np.linalg.pinv(model["covariance"]), residual))
    return pd.Series(value, index=table.index, name="context_adjusted_gait_deviation_v1")


def serialize(model: dict) -> dict:
    return {"feature_order": model["features"], "covariates": model["covariates"],
            "beta": np.asarray(model["beta"]).tolist(), "covariance": np.asarray(model["covariance"]).tolist(),
            "covariance_method": model["covariance_method"]}
