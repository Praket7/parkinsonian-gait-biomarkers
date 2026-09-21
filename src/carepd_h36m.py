"""Published CARE-PD Appendix-B features from official H36M joint assets.

The input is the official 30-Hz, z-forward/y-up/x-lateral H36M tensor; this
module never approximates joints from raw SMPL pose parameters.
"""
from __future__ import annotations

import numpy as np
from scipy.signal import find_peaks


LEFT_ANKLE, RIGHT_ANKLE, SACRUM = 6, 3, 0
MIN_PEAK_DISTANCE_FRAMES, MIN_PEAK_PROMINENCE = 8, 0.02


def extract_features(joints, fps=30.0):
    """Return four prespecified CARE features or a transparent QC status."""
    joints = np.asarray(joints, dtype=float)
    result = {"status": "NOT_ESTIMABLE", "qc_reason": "invalid_h36m_tensor"}
    if joints.ndim != 3 or joints.shape[1:] != (17, 3) or not np.isfinite(joints).all() or fps <= 0:
        return result
    distance = np.linalg.norm(joints[:, LEFT_ANKLE] - joints[:, RIGHT_ANKLE], axis=1)
    events, _ = find_peaks(distance, distance=MIN_PEAK_DISTANCE_FRAMES, prominence=MIN_PEAK_PROMINENCE)
    duration = (len(joints) - 1) / float(fps)
    if duration < 3 or len(events) < 4:
        return {**result, "qc_reason": "duration_or_heel_strikes_insufficient", "n_heel_strikes": int(len(events))}
    intervals = np.diff(events) / float(fps)
    step_length = np.abs(np.diff(joints[events, SACRUM, 2]))
    speed = np.abs(joints[events[-1], SACRUM, 2] - joints[events[0], SACRUM, 2]) / ((events[-1] - events[0]) / float(fps))
    values = {"gait_speed": float(speed), "cadence": float(len(events) / duration * 60),
              "step_length_mean": float(np.mean(step_length)), "step_time_mean": float(np.mean(intervals)),
              "n_heel_strikes": int(len(events)), "status": "OK", "qc_reason": "prespecified_qc_passed"}
    if not all(np.isfinite(list(values.values())[:4])) or not (40 <= values["cadence"] <= 200) or not (.2 <= values["gait_speed"] <= 3):
        return {**result, "qc_reason": "physiologic_range_failed", "n_heel_strikes": int(len(events))}
    return values
