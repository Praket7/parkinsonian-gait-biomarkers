from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.v4_6.score_agreement import score_agreement, score_matched_trials


def model() -> dict:
    return {
        "features": ["gait_speed", "step_length_mean", "stride_length_mean", "cadence",
                     "step_time_mean", "stride_time_mean", "step_time_cv", "stride_time_cv"],
        "covariates": ["age", "height_m"],
        "beta": np.zeros((3, 8)),
        "covariance": np.eye(8),
        "covariance_method": "sample",
    }


def matched() -> pd.DataFrame:
    rows = []
    base = [120.0, 65.0, 130.0, 110.0, 0.55, 1.10, 3.0, 2.0]
    features = model()["features"]
    for i in range(8):
        row = {"participant": f"P{i}", "task": "SelfPace", "age": 60.0 + i, "height_m": 1.7}
        for j, feature in enumerate(features):
            row[f"{feature}_pkmas"] = base[j] + i * (j + 1) * 0.1
            row[f"{feature}_raw"] = row[f"{feature}_pkmas"]
        rows.append(row)
    return pd.DataFrame(rows)


def test_identical_feature_sources_produce_identical_scores():
    pairs = score_matched_trials(matched(), model())
    assert np.allclose(pairs.score_pkmas, pairs.score_raw)
    result = score_agreement(pairs.score_pkmas.to_numpy(), pairs.score_raw.to_numpy())
    assert result["icc_a1"] == pytest.approx(1.0)
    assert result["ccc"] == pytest.approx(1.0)
    assert result["mean_bias"] == pytest.approx(0.0)
    assert result["mae"] == pytest.approx(0.0)
    assert result["rmse"] == pytest.approx(0.0)


def test_spatial_features_are_converted_from_cm_to_m_for_both_sources():
    pairs = score_matched_trials(matched(), model())
    first = matched().iloc[0]
    expected = np.array([first.gait_speed_pkmas / 100, first.step_length_mean_pkmas / 100,
                         first.stride_length_mean_pkmas / 100, first.cadence_pkmas,
                         first.step_time_mean_pkmas, first.stride_time_mean_pkmas,
                         first.step_time_cv_pkmas, first.stride_time_cv_pkmas])
    assert pairs.score_pkmas.iloc[0] == pytest.approx(np.linalg.norm(expected))


def test_nonidentical_sources_report_nonzero_error_and_finite_agreement():
    table = matched()
    table.loc[0, "gait_speed_raw"] += 10.0
    pairs = score_matched_trials(table, model())
    result = score_agreement(pairs.score_pkmas.to_numpy(), pairs.score_raw.to_numpy())
    assert result["mae"] > 0
    assert result["rmse"] > 0
    assert np.isfinite(result["icc_a1"])
    assert result["n"] == len(table)


def test_missing_required_feature_pair_is_rejected():
    table = matched().drop(columns=["cadence_raw"])
    with pytest.raises(ValueError, match="missing"):
        score_matched_trials(table, model())
