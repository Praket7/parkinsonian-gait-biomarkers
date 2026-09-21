"""Control-only context-adjusted deviation score."""
from __future__ import annotations
import numpy as np
import pandas as pd


def fit_controls(controls: pd.DataFrame, features, covariates=("age", "height_m")):
    """Fit linear reference models and a ridge-stabilized residual covariance in controls only."""
    if controls.empty or controls.get("clinical_cohort", pd.Series()).astype(str).str.lower().eq("pd").any():
        raise ValueError("normative model accepts controls only")
    x = np.column_stack([np.ones(len(controls)), *[pd.to_numeric(controls[c], errors="coerce") for c in covariates]])
    valid = np.isfinite(x).all(axis=1) & controls[list(features)].notna().all(axis=1)
    x, y = x[valid], controls.loc[valid, features].to_numpy(float)
    if len(x) <= len(covariates)+2: raise ValueError("insufficient control observations")
    beta = np.linalg.lstsq(x, y, rcond=None)[0]; residuals = y - x @ beta
    covariance = np.cov(residuals, rowvar=False); covariance = np.atleast_2d(covariance) + np.eye(len(features))*1e-6
    return {"features": list(features), "covariates": list(covariates), "beta": beta, "covariance": covariance, "residual_sd": residuals.std(axis=0, ddof=1)}


def score(table: pd.DataFrame, model):
    x = np.column_stack([np.ones(len(table)), *[pd.to_numeric(table[c], errors="coerce") for c in model["covariates"]]])
    observed = table[model["features"]].to_numpy(float); residual = observed - x @ model["beta"]
    inverse = np.linalg.pinv(model["covariance"])
    return pd.Series(np.sqrt(np.einsum("ij,jk,ik->i", residual, inverse, residual)), index=table.index, name="context_adjusted_gait_deviation_v1")
