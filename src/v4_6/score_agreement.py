"""Endpoint-level analytical agreement for the frozen v4.1 gait deviation score."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.v4_1.normative import score
from src.v4_2.analytical_equivalence import agreement

SPATIAL_CM_FEATURES = {"gait_speed", "step_length_mean", "stride_length_mean"}


def icc_a1(reference: np.ndarray, candidate: np.ndarray) -> float:
    """Two-way absolute-agreement single-measure ICC(A,1)."""
    values = np.column_stack((np.asarray(reference, float), np.asarray(candidate, float)))
    if values.ndim != 2 or values.shape[0] < 2 or not np.isfinite(values).all():
        raise ValueError("ICC requires at least two complete finite pairs")
    n, k = values.shape
    row_means = values.mean(axis=1)
    column_means = values.mean(axis=0)
    grand = values.mean()
    ms_rows = k * np.square(row_means - grand).sum() / (n - 1)
    ms_columns = n * np.square(column_means - grand).sum() / (k - 1)
    residual = values - row_means[:, None] - column_means[None, :] + grand
    ms_error = np.square(residual).sum() / ((n - 1) * (k - 1))
    denominator = ms_rows + (k - 1) * ms_error + k * (ms_columns - ms_error) / n
    return float((ms_rows - ms_error) / denominator) if denominator else float("nan")


def _source_table(matched: pd.DataFrame, model: dict, suffix: str) -> pd.DataFrame:
    required = [*model["covariates"], *[f"{feature}_{suffix}" for feature in model["features"]]]
    missing = [name for name in required if name not in matched]
    if missing:
        raise ValueError(f"missing matched score columns: {missing}")
    result = matched.loc[:, model["covariates"]].copy()
    for feature in model["features"]:
        values = pd.to_numeric(matched[f"{feature}_{suffix}"], errors="coerce").astype(float)
        if feature in SPATIAL_CM_FEATURES:
            values = values / 100.0
        result[feature] = values
    return result


def score_matched_trials(matched: pd.DataFrame, model: dict) -> pd.DataFrame:
    """Score PKMAS and independently reconstructed features under one frozen model."""
    pkmas = _source_table(matched, model, "pkmas")
    raw = _source_table(matched, model, "raw")
    output = pd.DataFrame(index=matched.index)
    for column in ("participant", "task"):
        if column in matched:
            output[column] = matched[column].values
    output["score_pkmas"] = score(pkmas, model).to_numpy(float)
    output["score_raw"] = score(raw, model).to_numpy(float)
    return output


def score_agreement(reference: np.ndarray, candidate: np.ndarray) -> dict[str, float]:
    """Agreement suite; correlation is retained only as secondary evidence."""
    pairs = pd.DataFrame({"reference": reference, "candidate": candidate}).apply(pd.to_numeric, errors="coerce").dropna()
    if len(pairs) < 2:
        raise ValueError("at least two complete score pairs are required")
    x = pairs.reference.to_numpy(float)
    y = pairs.candidate.to_numpy(float)
    result = agreement(x, y)
    result["icc_a1"] = icc_a1(x, y)
    return result
