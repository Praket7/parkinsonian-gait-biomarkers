"""Outcome-blind turning phenotypes from an already validated yaw trace."""
from __future__ import annotations
import numpy as np


def turning_features(yaw_velocity, sampling_hz, *, threshold=30.0):
    v = np.asarray(yaw_velocity, float)
    if len(v) < 2 or sampling_hz <= 0 or not np.isfinite(v).all(): return {"status": "NOT_ESTIMABLE", "reason": "SENSOR_QC_INSUFFICIENT"}
    active = abs(v) >= threshold
    if not active.any(): return {"status": "NOT_ESTIMABLE", "reason": "TURN_NOT_DETECTED"}
    duration = active.sum()/sampling_hz; angle = abs(v[active]).sum()/sampling_hz
    return {"status": "OK", "turn_duration_v1": float(duration), "peak_yaw_velocity_v1": float(abs(v).max()), "turn_angle_per_step_v1": float(angle), "turn_step_count_v1": np.nan, "turn_step_duration_v1": np.nan}
