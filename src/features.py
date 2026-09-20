import numpy as np
import pandas as pd


FEATURE_REGISTRY = {
    "cadence": {"units": "steps/min", "source": "contacts", "family": "rhythm"},
    "step_time_mean": {"units": "s", "source": "contacts", "family": "rhythm"},
    "step_time_cv": {"units": "%", "source": "contacts", "family": "variability"},
    "stride_time_mean": {"units": "s", "source": "contacts", "family": "rhythm"},
    "stride_time_cv": {"units": "%", "source": "contacts", "family": "variability"},
    "stance_fraction": {"units": "fraction", "source": "events", "family": "stance_swing"},
    "swing_fraction": {"units": "fraction", "source": "events", "family": "stance_swing"},
    "step_length_mean": {"units": "m", "source": "walkway", "family": "pace"},
    "step_length_cv": {"units": "%", "source": "walkway", "family": "variability"},
    "gait_speed": {"units": "m/s", "source": "walkway", "family": "pace"},
    "step_time_asymmetry": {"units": "%", "source": "contacts", "family": "asymmetry"},
    "step_length_asymmetry": {"units": "%", "source": "walkway", "family": "asymmetry"},
    "arm_swing_rom": {"units": "deg", "source": "wrist/trunk", "family": "arm"},
    "arm_swing_asymmetry": {"units": "%", "source": "wrist/trunk", "family": "arm"},
    "trunk_accel_rms": {"units": "m/s2", "source": "trunk", "family": "trunk"},
}


def _clean(x):
    a = np.asarray(x, dtype=float)
    return a[np.isfinite(a)]


def _cv(x):
    x = _clean(x)
    return float(100 * np.std(x, ddof=1) / np.mean(x)) if len(x) > 1 and np.mean(x) else np.nan


def _asymmetry(left, right):
    left, right = _clean(left), _clean(right)
    if not len(left) or not len(right):
        return np.nan
    l, r = np.mean(left), np.mean(right)
    return float(100 * abs(l - r) / ((l + r) / 2)) if np.isfinite(l + r) and (l + r) else np.nan


def extract_bout_features(bout):
    """Derive interpretable features from one bout/event dictionary.

    Contact arrays are timestamps in seconds. Optional arrays may be supplied
    by walkway/insole/IMU adapters using the names documented in the registry.
    """
    left = _clean(bout.get("left_contacts", []))
    right = _clean(bout.get("right_contacts", []))
    contacts = np.sort(np.r_[left, right])
    step = np.diff(contacts)
    stride = np.diff(left) if len(left) > 1 else np.diff(right)
    step_mean = np.mean(step) if len(step) else np.nan
    stance = _clean(bout.get("stance_time", []))
    stride_all = _clean(bout.get("stride_time", []))
    fraction = stance[:min(len(stance), len(stride_all))] / stride_all[:min(len(stance), len(stride_all))] if len(stance) and len(stride_all) else []
    swing = _clean(bout.get("swing_time", []))
    n_fraction = min(len(swing), len(stride_all))
    out = {
        "cadence": float(60 / step_mean) if step_mean > 0 else np.nan,
        "step_time_mean": float(step_mean) if len(step) else np.nan,
        "step_time_cv": _cv(step),
        "stride_time_mean": float(np.mean(stride)) if len(stride) else np.nan,
        "stride_time_cv": _cv(stride),
        "stance_fraction": float(np.nanmean(fraction)) if len(fraction) else np.nan,
        "swing_fraction": float(np.nanmean(swing[:n_fraction] / stride_all[:n_fraction])) if n_fraction else np.nan,
        "step_length_mean": float(np.nanmean(_clean(bout.get("step_length", [])))) if len(_clean(bout.get("step_length", []))) else np.nan,
        "step_length_cv": _cv(bout.get("step_length", [])),
        "gait_speed": float(bout["gait_speed"]) if bout.get("gait_speed") is not None else np.nan,
        "step_time_asymmetry": _asymmetry(bout.get("left_step_time", []), bout.get("right_step_time", [])),
        "step_length_asymmetry": _asymmetry(bout.get("left_step_length", []), bout.get("right_step_length", [])),
        "arm_swing_rom": float(bout["arm_swing_rom"]) if bout.get("arm_swing_rom") is not None else np.nan,
        "arm_swing_asymmetry": float(bout["arm_swing_asymmetry"]) if bout.get("arm_swing_asymmetry") is not None else np.nan,
        "trunk_accel_rms": float(bout["trunk_accel_rms"]) if bout.get("trunk_accel_rms") is not None else np.nan,
    }
    return out


def aggregate_bouts(frame):
    """Aggregate already-derived bout rows to the principal participant-task unit."""
    keys = [k for k in ("participant_id", "site", "session_id", "task") if k in frame]
    if not keys:
        raise ValueError("feature table needs participant_id and task")
    numeric = [c for c in FEATURE_REGISTRY if c in frame]
    grouped = frame.groupby(keys, dropna=False)
    result = grouped[numeric].mean().reset_index()
    metadata = [c for c in frame.columns if c not in keys + numeric and c not in {"source_file"}]
    if metadata:
        first = grouped[metadata].first().reset_index(drop=True)
        result = pd.concat([result, first], axis=1)
    return result
