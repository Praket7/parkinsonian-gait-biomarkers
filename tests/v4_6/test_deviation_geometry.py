from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.v4_1.normative import score
from src.v4_6.deviation_geometry import (
    conditional_residual,
    deviation_magnitude,
    precision_angle,
    precision_cosine,
    precision_matrix,
)


def model() -> dict:
    return {
        "features": ["f1", "f2"],
        "covariates": ["age", "height_m"],
        "beta": np.array([[1.0, -1.0], [0.1, 0.2], [0.5, -0.5]]),
        "covariance": np.array([[4.0, 0.0], [0.0, 1.0]]),
        "covariance_method": "sample",
    }


def table() -> pd.DataFrame:
    return pd.DataFrame({"age": [60.0, 70.0], "height_m": [1.7, 1.8], "f1": [9.0, 10.0], "f2": [8.0, 9.0]})


def test_precision_matrix_is_covariance_pseudoinverse():
    expected = np.linalg.pinv(model()["covariance"])
    assert np.allclose(precision_matrix(model()), expected)


def test_conditional_residual_matches_frozen_score_geometry():
    fitted = model()
    residuals = conditional_residual(table(), fitted)
    precision = precision_matrix(fitted)
    magnitudes = np.array([deviation_magnitude(row, precision) for row in residuals])
    assert np.allclose(magnitudes, score(table(), fitted).to_numpy())
    assert np.allclose(np.square(magnitudes), np.einsum("ij,jk,ik->i", residuals, precision, residuals))


def test_identical_direction_is_positive_one():
    p = np.diag([0.25, 1.0])
    a = np.array([2.0, 3.0])
    assert precision_cosine(a, a, p) == pytest.approx(1.0)


def test_opposite_direction_is_negative_one():
    p = np.diag([0.25, 1.0])
    a = np.array([2.0, 3.0])
    assert precision_cosine(a, -a, p) == pytest.approx(-1.0)


def test_precision_orthogonal_vectors_have_zero_cosine():
    p = np.diag([0.25, 1.0])
    assert precision_cosine(np.array([2.0, 0.0]), np.array([0.0, 4.0]), p) == pytest.approx(0.0)
    assert precision_angle(np.array([2.0, 0.0]), np.array([0.0, 4.0]), p) == pytest.approx(np.pi / 2)


def test_positive_scale_does_not_change_direction_similarity():
    p = np.array([[2.0, 0.3], [0.3, 1.0]])
    a, b = np.array([1.0, 2.0]), np.array([3.0, -0.5])
    expected = precision_cosine(a, b, p)
    assert precision_cosine(7.0 * a, 0.2 * b, p) == pytest.approx(expected)


def test_zero_residual_is_not_coerced_to_zero_similarity():
    p = np.eye(2)
    value = precision_cosine(np.zeros(2), np.ones(2), p)
    assert np.isnan(value)
    assert np.isnan(precision_angle(np.zeros(2), np.ones(2), p))


def test_dimension_mismatch_is_rejected():
    with pytest.raises(ValueError):
        precision_cosine(np.ones(2), np.ones(3), np.eye(2))
