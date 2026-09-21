"""Frozen SP-to-HP motor-scaling phenotypes."""
from __future__ import annotations
import numpy as np
import pandas as pd


def response_indices(table: pd.DataFrame, *, minimum_delta_speed=.05):
    needed = {"participant_id", "task", "gait_speed", "stride_length_mean", "cadence"}
    if not needed.issubset(table): return pd.DataFrame()
    wide = table[table.task.isin(["SP", "HP"])].pivot_table(index="participant_id", columns="task", values=["gait_speed", "stride_length_mean", "cadence"], aggfunc="mean")
    if not {"SP", "HP"}.issubset(wide.columns.get_level_values(1)): return pd.DataFrame()
    ds = wide[("gait_speed", "HP")] - wide[("gait_speed", "SP")]
    out = pd.DataFrame({"participant_id": wide.index, "delta_speed": ds,
        "stride_scaling_response_v1": (wide[("stride_length_mean", "HP")] - wide[("stride_length_mean", "SP")]) / ds,
        "cadence_scaling_response_v1": (wide[("cadence", "HP")] - wide[("cadence", "SP")]) / ds}).reset_index(drop=True)
    return out.where(out.delta_speed.abs().ge(minimum_delta_speed), np.nan)
