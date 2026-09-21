"""Outcome-blind trunk smoothness calculation."""
from __future__ import annotations
import numpy as np


def axial_rotation_smoothness(yaw_velocity, sampling_hz):
    signal = np.asarray(yaw_velocity, float)
    if len(signal) < 32 or sampling_hz <= 0 or not np.isfinite(signal).all():
        return {"status": "NOT_ESTIMABLE", "reason": "SENSOR_QC_INSUFFICIENT"}
    spectrum = abs(np.fft.rfft(signal - signal.mean())); freq = np.fft.rfftfreq(len(signal), 1/sampling_hz)
    use = (freq > 0) & (freq <= 10) & (spectrum > 0)
    return {"status": "OK", "axial_rotation_smoothness_v1": float(-np.trapz(np.sqrt(1 + np.diff(np.log(spectrum[use]))**2), np.log(freq[use])[1:])) if use.sum() > 2 else np.nan}
