"""Outcome-blind control-reference model used by the v4.1 validation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf


FEATURES = ("gait_speed", "cadence", "step_length_mean", "stride_length_mean",
            "step_time_mean", "stride_time_mean", "step_time_cv", "stride_time_cv")
COVARIATES = ("age", "height_m")
FROZEN_MODEL_SHA256 = "b3d04cc17a08de4c213abe3d01f7d378b161a75df847da8022659c11312dfb53"


def load_frozen_model(path: str | Path) -> dict:
    """Load the released reference, rejecting missing or altered artifacts."""
    payload = Path(path).read_bytes()
    if hashlib.sha256(payload).hexdigest() != FROZEN_MODEL_SHA256:
        raise ValueError("frozen v4.1 reference SHA256 mismatch")
    model = json.loads(payload)
    model["features"] = model.pop("feature_order")
    if tuple(model["features"]) != FEATURES or tuple(model["covariates"]) != COVARIATES:
        raise ValueError("frozen v4.1 reference feature contract mismatch")
    model["beta"] = np.asarray(model["beta"], dtype=float)
    model["covariance"] = np.asarray(model["covariance"], dtype=float)
    return model


def fit_reference(controls: pd.DataFrame, features=FEATURES, covariance_method="sample") -> dict:
    """Fit the declared reference using control observations only."""
    if controls.empty or controls.get("clinical_cohort", pd.Series(dtype=str)).astype(str).str.lower().eq("pd").any():
        raise ValueError("reference fitting accepts controls only")
    features = list(features)
    x = np.column_stack([np.ones(len(controls)), *[pd.to_numeric(controls[c], errors="coerce") for c in COVARIATES]])
    valid = np.isfinite(x).all(axis=1) & controls[features].notna().all(axis=1)
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
