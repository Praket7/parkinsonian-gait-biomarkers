"""Outcome-blind bilateral arm coordination functions."""
from __future__ import annotations
import numpy as np


def arm_features(left, right):
    left, right = np.asarray(left, float), np.asarray(right, float)
    n = min(len(left), len(right)); left, right = left[:n], right[:n]
    if n < 20 or not np.isfinite(left).all() or not np.isfinite(right).all():
        return {"status": "NOT_ESTIMABLE", "reason": "SENSOR_QC_INSUFFICIENT"}
    lrom, rrom = np.ptp(left), np.ptp(right); denom = .5 * (lrom + rrom)
    corr = np.correlate((left-left.mean())/(left.std() or np.nan), (right-right.mean())/(right.std() or np.nan), mode="full") / n
    return {"status": "OK", "arm_swing_rom_v1": float((lrom+rrom)/2),
            "arm_swing_asymmetry_v1": float(abs(lrom-rrom)/denom) if denom else np.nan,
            "arm_swing_coordination_v1": float(np.nanmax(abs(corr)))}
