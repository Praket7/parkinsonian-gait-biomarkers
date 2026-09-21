"""Long-bout temporal variability, independent of clinical outcomes."""
from __future__ import annotations
import numpy as np
from .gait_events import event_qc


def _cv(values):
    values = np.asarray(values, float); values = values[np.isfinite(values)]
    return float(100 * values.std(ddof=1) / values.mean()) if len(values) > 1 and values.mean() > 0 else np.nan


def longbout_variability(left, right, *, minimum_cycles=30, interval_min=.25, interval_max=2.0):
    qc = event_qc(left, right, minimum_cycles=minimum_cycles, minimum=interval_min, maximum=interval_max)
    times, labels = qc.pop("times"), qc.pop("labels")
    step = np.diff(times)
    stride = np.diff(times[labels == 0])
    return {**qc, "step_time_cv_longbout_v1": _cv(step), "stride_time_cv_longbout_v1": _cv(stride)}


def convergence_errors(intervals, grid=(5, 10, 15, 20, 25, 30, 40, 50)):
    """Relative CV error against the complete recording at each prespecified k."""
    intervals = np.asarray(intervals, float); intervals = intervals[np.isfinite(intervals)]
    full = _cv(intervals); rows = []
    for k in grid:
        if k <= len(intervals) and np.isfinite(full) and full:
            rows.append({"n_cycles": int(k), "relative_error": abs(_cv(intervals[:k]) - full) / abs(full)})
    return rows


def choose_minimum_cycles(errors, *, median_max=.10, p90_max=.20):
    """Select the first frozen grid value satisfying precision across recordings."""
    for k in sorted({row["n_cycles"] for row in errors}):
        values = [row["relative_error"] for row in errors if row["n_cycles"] == k]
        if values and np.median(values) <= median_max and np.quantile(values, .9) <= p90_max:
            return int(k)
    return None
