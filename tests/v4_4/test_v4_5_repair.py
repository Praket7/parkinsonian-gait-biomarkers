import numpy as np
import pandas as pd
import pytest

from scripts.run_v4_5_repair import analyze, describe_instability, endpoint_resampling
from src.v4_1.normative import load_frozen_model
from src.v4_2.repeated_group_cv import favorable_fraction
from src.v4_3.walkway_reconstruction import FEATURES


def test_frozen_model_rejects_tampering(tmp_path):
    original = "results/v4_1/frozen/v4_1_control_model.json"
    assert load_frozen_model(original)["features"] == list(FEATURES)
    altered = tmp_path / "model.json"
    altered.write_bytes(open(original, "rb").read() + b" ")
    with pytest.raises(ValueError, match="SHA256"):
        load_frozen_model(altered)


def test_calibration_favorability_uses_distance_to_target():
    rows = pd.DataFrame({"baseline_calibration_slope": [.9, 1.1], "extended_calibration_slope": [1.05, 1.3],
                         "baseline_calibration_intercept": [.3, -.2], "extended_calibration_intercept": [.1, -.4]})
    assert favorable_fraction(rows, "calibration_slope") == .5
    assert favorable_fraction(rows, "calibration_intercept") == .5


def test_endpoint_bootstrap_is_finite_and_requires_four_passes():
    model = load_frozen_model("results/v4_1/frozen/v4_1_control_model.json")
    rows = pd.DataFrame([{**dict(zip(FEATURES, [100+i, 100+i, 60+i, 120+i, .6, 1.2, 2, 2])), "age": 70, "height_m": 1.7}
                         for i in range(4)])
    assert np.isfinite(endpoint_resampling(rows, model, 9, 50))
    with pytest.raises(ValueError, match="four"):
        endpoint_resampling(rows.iloc[:3], model, 9)


def test_duplicate_endpoint_fails_closed():
    model = load_frozen_model("results/v4_1/frozen/v4_1_control_model.json")
    endpoints = pd.DataFrame([{"participant": "a", "session": "1", "task": "SelfPace", "score": 1.0}] * 2)
    with pytest.raises(ValueError, match="duplicate"):
        analyze(pd.DataFrame(), endpoints, model)


def test_instability_keeps_person_visit_pass_and_task_units_distinct():
    endpoints = pd.DataFrame([{"participant": person, "session": session, "task": task,
                               "score": offset + (session == "2") + (task == "HurriedPace") * .5}
                              for person, offset in (("a", 0), ("b", 2))
                              for session in ("1", "2") for task in ("SelfPace", "HurriedPace")])
    passes = pd.DataFrame([{"participant": row.participant, "session": row.session, "task": row.task,
                            "score": row.score + shift} for row in endpoints.itertuples()
                           for shift in (-.3, -.1, .1, .3)])
    result = describe_instability(passes, endpoints).set_index("task")
    assert result.loc["SelfPace", "n_paired"] == 2
    assert result.loc["SelfPace", "n_paired_task_sessions"] == 4
    assert result.loc["HurriedPace", "hurried_minus_self_mean"] == pytest.approx(.5)
    assert result.loc["SelfPace", "within_session_pass_score_sd"] > 0
