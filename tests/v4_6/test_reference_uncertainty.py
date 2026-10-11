from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.v4_6.reference_uncertainty import reference_bootstrap, resample_controls_by_participant


FEATURES = ["f1", "f2"]


def controls() -> pd.DataFrame:
    rows = []
    for i in range(8):
        for repeat in range(2):
            rows.append({"participant_id": f"C{i}", "clinical_cohort": "control", "age": 50 + i,
                         "height_m": 1.6 + 0.02 * i,
                         "f1": 0.1 * i + 0.01 * repeat,
                         "f2": -0.05 * i + 0.02 * repeat})
    return pd.DataFrame(rows)


def endpoints() -> pd.DataFrame:
    rows = []
    for task in ("SelfPace", "HurriedPace"):
        for i in range(5):
            for session, shift in (("1", 0.0), ("2", 0.08)):
                rows.append({"participant": f"P{i}", "session": session, "task": task,
                             "age": 63 + i, "height_m": 1.7,
                             "f1": 0.7 + 0.2 * i + shift,
                             "f2": -0.4 + 0.1 * i - shift / 2})
    return pd.DataFrame(rows)


def test_control_bootstrap_resamples_whole_participants_with_unique_ids():
    rng = np.random.default_rng(10)
    sampled = resample_controls_by_participant(controls(), rng)
    assert len(sampled) == len(controls())
    assert sampled.participant_id.nunique() == controls().participant_id.nunique()
    assert sampled.participant_id.str.startswith("control_boot_").all()
    assert set(sampled.clinical_cohort) == {"control"}
    assert sampled.groupby("participant_id").size().eq(2).all()


def test_reference_bootstrap_is_deterministic_and_uses_same_reference_for_both_sessions():
    first, people_first = reference_bootstrap(controls(), endpoints(), FEATURES, iterations=9, seed=23,
                                               covariance_method="sample")
    second, people_second = reference_bootstrap(controls(), endpoints(), FEATURES, iterations=9, seed=23,
                                                 covariance_method="sample")
    pd.testing.assert_frame_equal(first, second)
    pd.testing.assert_frame_equal(people_first, people_second)
    assert first["resample"].nunique() == 9
    assert set(first.task) == {"SelfPace", "HurriedPace"}
    assert {"icc_a1", "median_precision_cosine", "mean_score_change", "median_score_change"}.issubset(first.columns)
    assert people_first.groupby(["resample", "task"]).participant.nunique().eq(5).all()


def test_pd_rows_are_rejected_from_reference_fitting():
    bad = controls()
    bad.loc[0, "clinical_cohort"] = "pd"
    with pytest.raises(ValueError, match="controls only"):
        reference_bootstrap(bad, endpoints(), FEATURES, iterations=2, seed=1, covariance_method="sample")


def test_duplicate_longitudinal_endpoint_is_rejected():
    bad = pd.concat([endpoints(), endpoints().iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate"):
        reference_bootstrap(controls(), bad, FEATURES, iterations=2, seed=1, covariance_method="sample")
