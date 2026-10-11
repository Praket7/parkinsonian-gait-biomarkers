from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.v4_6.longitudinal_direction import (
    holm_adjust,
    pair_direction_rows,
    participant_bootstrap,
    permutation_null,
)


def model() -> dict:
    return {
        "features": ["f1", "f2"],
        "covariates": ["age", "height_m"],
        "beta": np.zeros((3, 2)),
        "covariance": np.eye(2),
        "covariance_method": "sample",
    }


def endpoints() -> pd.DataFrame:
    rows = []
    values = {
        "SelfPace": {"A": ([1.0, 0.0], [1.1, 0.1]), "B": ([0.0, 1.0], [0.1, 1.1]), "C": ([-1.0, 0.0], [-0.9, -0.1])},
        "HurriedPace": {"A": ([1.0, 1.0], [1.2, 0.9]), "B": ([-1.0, 1.0], [-0.8, 1.1]), "C": ([1.0, -1.0], [0.9, -1.2])},
    }
    for task, people in values.items():
        for participant, (first, second) in people.items():
            for session, value in (("1", first), ("2", second)):
                rows.append({"participant": participant, "session": session, "task": task,
                             "age": 65.0, "height_m": 1.75, "f1": value[0], "f2": value[1]})
    return pd.DataFrame(rows)


def test_pairs_only_same_participant_and_task():
    pairs = pair_direction_rows(endpoints(), model(), tasks=["SelfPace", "HurriedPace"])
    assert len(pairs) == 6
    assert set(pairs.task) == {"SelfPace", "HurriedPace"}
    assert pairs.groupby("task").participant.nunique().to_dict() == {"HurriedPace": 3, "SelfPace": 3}
    assert pairs.precision_cosine.between(-1, 1).all()


def test_incomplete_participant_is_excluded_not_imputed():
    table = endpoints()
    table = table[~((table.participant == "C") & (table.task == "SelfPace") & (table.session == "2"))]
    pairs = pair_direction_rows(table, model(), tasks=["SelfPace"])
    assert set(pairs.participant) == {"A", "B"}


def test_duplicate_participant_session_task_is_rejected():
    table = pd.concat([endpoints(), endpoints().iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate"):
        pair_direction_rows(table, model(), tasks=["SelfPace"])


def test_participant_bootstrap_is_deterministic_and_has_requested_size():
    values = np.array([0.1, 0.4, 0.8, 0.9])
    first = participant_bootstrap(values, iterations=31, seed=17)
    second = participant_bootstrap(values, iterations=31, seed=17)
    assert len(first) == 31
    assert np.array_equal(first, second)


def test_permutation_null_is_within_task_deterministic_and_requested_size():
    first = permutation_null(endpoints(), model(), task="SelfPace", iterations=37, seed=19)
    second = permutation_null(endpoints(), model(), task="SelfPace", iterations=37, seed=19)
    assert len(first) == 37
    assert np.array_equal(first, second)
    assert np.isfinite(first).all()


def test_holm_adjust_exact_two_primary_tests():
    adjusted = holm_adjust({"SelfPace": 0.01, "HurriedPace": 0.04})
    assert adjusted["SelfPace"] == pytest.approx(0.02)
    assert adjusted["HurriedPace"] == pytest.approx(0.04)


def test_zero_magnitude_direction_is_counted_and_excluded():
    table = endpoints()
    mask = (table.participant == "A") & (table.task == "SelfPace") & (table.session == "1")
    table.loc[mask, ["f1", "f2"]] = 0.0
    pairs = pair_direction_rows(table, model(), tasks=["SelfPace"])
    a = pairs.loc[pairs.participant.eq("A")].iloc[0]
    assert np.isnan(a.precision_cosine)
    assert bool(a.direction_estimable) is False
