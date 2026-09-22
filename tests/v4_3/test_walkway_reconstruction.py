import pandas as pd
import pytest

from src.v4_3.walkway_reconstruction import initial_footfalls, summarize_footfalls


def test_documented_cell_coordinates_reconstruct_eight_inputs():
    table = pd.DataFrame({
        "Time": ["0 sec", ".5 sec", "1 sec", "1.5 sec", "2 sec"],
        "GeneralEvent": ["Walk"] * 5,
        "L Foot Contact": [1, 0, 1, 0, 1],
        "R Foot Contact": [0, 1, 0, 1, 0],
        "Walkway_X": ["0|0", "10|10", "20|20", "30|30", "40|40"],
        "Walkway_Y": ["1|2"] * 5,
        "WalkwayFoot": ["L|L", "R|R", "L|L", "R|R", "L|L"],
    })
    result = summarize_footfalls(initial_footfalls(table))
    assert result["step_length_mean"] == pytest.approx(12.7)
    assert result["stride_length_mean"] == pytest.approx(25.4)
    assert result["step_time_mean"] == pytest.approx(0.5)
    assert result["stride_time_mean"] == pytest.approx(1.0)
    assert result["cadence"] == pytest.approx(120.0)

