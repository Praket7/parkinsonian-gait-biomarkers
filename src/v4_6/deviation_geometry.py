"""Geometry of the frozen healthy-reference gait deviation without changing its score."""
from __future__ import annotations

import numpy as np
import pandas as pd


def conditional_residual(table: pd.DataFrame, model: dict) -> np.ndarray:
    """Return x - E_control[x | covariates] in the model's frozen feature order."""
    missing = [name for name in (*model["covariates"], *model["features"]) if name not in table]
    if missing:
        raise ValueError(f"missing model columns: {missing}")
    design = np.column_stack(
        [np.ones(len(table)), *[pd.to_numeric(table[name], errors="coerce") for name in model["covariates"]]]
    )
    observed = table[model["features"]].apply(pd.to_numeric, errors="coerce").to_numpy(float)
    expected = design @ np.asarray(model["beta"], dtype=float)
    return observed - expected


def precision_matrix(model: dict) -> np.ndarray:
    """Moore-Penrose precision matrix used by the historical v4.1 score."""
    covariance = np.asarray(model["covariance"], dtype=float)
    if covariance.ndim != 2 or covariance.shape[0] != covariance.shape[1]:
        raise ValueError("covariance must be square")
    return np.linalg.pinv(covariance)


def _vector(value: np.ndarray) -> np.ndarray:
    vector = np.asarray(value, dtype=float)
    if vector.ndim != 1:
        raise ValueError("deviation vector must be one dimensional")
    return vector


def deviation_magnitude(residual: np.ndarray, precision: np.ndarray) -> float:
    """Return sqrt(r'Pr), exactly the geometry of the frozen scalar score."""
    residual = _vector(residual)
    precision = np.asarray(precision, dtype=float)
    if precision.shape != (len(residual), len(residual)):
        raise ValueError("precision matrix dimension mismatch")
    quadratic = float(residual @ precision @ residual)
    if quadratic < 0 and np.isclose(quadratic, 0.0, atol=1e-12):
        quadratic = 0.0
    if quadratic < 0:
        raise ValueError("precision quadratic form is negative")
    return float(np.sqrt(quadratic))


def precision_cosine(a: np.ndarray, b: np.ndarray, precision: np.ndarray, *, atol: float = 1e-12) -> float:
    """Cosine between deviation vectors under the frozen healthy precision metric.

    A zero/degenerate vector has no direction and returns NaN rather than being
    silently interpreted as orthogonal.
    """
    a, b = _vector(a), _vector(b)
    if a.shape != b.shape:
        raise ValueError("deviation vector dimension mismatch")
    precision = np.asarray(precision, dtype=float)
    if precision.shape != (len(a), len(a)):
        raise ValueError("precision matrix dimension mismatch")
    aa = float(a @ precision @ a)
    bb = float(b @ precision @ b)
    if aa <= atol or bb <= atol:
        return float("nan")
    value = float((a @ precision @ b) / np.sqrt(aa * bb))
    return float(np.clip(value, -1.0, 1.0))


def precision_angle(a: np.ndarray, b: np.ndarray, precision: np.ndarray) -> float:
    """Return the precision-metric angle in radians, or NaN if direction is undefined."""
    cosine = precision_cosine(a, b, precision)
    return float(np.arccos(cosine)) if np.isfinite(cosine) else float("nan")
