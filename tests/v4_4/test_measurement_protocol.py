import pandas as pd
import pytest

from src.v4_3.walkway_reconstruction import FEATURES
from src.v4_4.measurement_protocol import median_pass_endpoint, variance_components


def _passes():
    rows = []
    for person, offset in (("a", 0.0), ("b", 5.0)):
        for session in ("1", "2"):
            for passage in range(1, 5):
                rows.append({"participant": person, "session": session, "pass": passage, "score": offset + (session == "2") + passage / 10})
    return pd.DataFrame(rows)


def test_median_endpoint_requires_every_declared_pass():
    frame = pd.DataFrame([{feature: value for feature in FEATURES} for value in range(4)])
    assert median_pass_endpoint(frame, 4)["cadence"] == 1.5
    with pytest.raises(ValueError): median_pass_endpoint(frame.iloc[:3], 4)


def test_variance_components_reports_absolute_error_for_balanced_protocol():
    result = variance_components(_passes())
    assert result["n_passes"] == 4
    assert result["sem"] > 0
    assert result["mdc95"] > result["sem"]
    assert 0 <= result["generalizability_coefficient"] <= 1
