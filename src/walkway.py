"""Reader for the released PKMAS reference-walkway summary table.

The source CSV has two header rows.  This adapter uses the documented mean/CV
columns only, retaining the pressure-walkway values as the primary reference
measurements rather than attempting to infer spatial quantities from IMUs.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .io import canonical_task, derive_site


_COLUMNS = {
    "Task|": "task",
    "Participant ID|": "participant_id",
    "PD vs Control|": "pd_status",
    "Step Length (cm.)|Mean": "step_length_mean",
    "Step Length (cm.)|%CV": "step_length_cv",
    "Velocity (cm./sec.)|": "gait_speed",
    "Stride Length (cm.)|Mean": "stride_length_mean",
    "Step Time (sec.)|Mean": "step_time_mean",
    "Step Time (sec.)|%CV": "step_time_cv",
    "Stride Time (sec.)|Mean": "stride_time_mean",
    "Stride Time (sec.)|%CV": "stride_time_cv",
    "Stance %|Mean": "stance_fraction",
    "Swing %|Mean": "swing_fraction",
    "Total D. Support %|Mean": "double_support_fraction",
    "Cadence (steps/min.)|": "cadence",
}


def load_walkway_metrics(path) -> pd.DataFrame:
    """Return one normalized, auditable reference row per participant and task."""
    path = Path(path)
    headers = pd.read_csv(path, header=None, nrows=2).fillna("")
    names = [f"{top}|{sub}" for top, sub in zip(headers.iloc[0], headers.iloc[1])]
    source = pd.read_csv(path, header=None, skiprows=2, names=names, low_memory=False)
    missing = set(_COLUMNS) - set(source.columns)
    if missing:
        raise ValueError(f"{path}: missing expected walkway columns {sorted(missing)}")
    result = source[list(_COLUMNS)].rename(columns=_COLUMNS).copy()
    result["participant_id"] = result["participant_id"].astype(str).str.strip()
    result["task"] = result["task"].map(canonical_task)
    result["site"] = result["participant_id"].map(derive_site)
    result["session_id"] = "v1"
    result["source_file"] = str(path)
    for column in result.columns:
        if column not in {"participant_id", "task", "pd_status", "site", "session_id", "source_file"}:
            result[column] = pd.to_numeric(result[column], errors="coerce")
    for column in ("step_length_mean", "stride_length_mean"):
        result[column] = result[column] / 100
    result["gait_speed"] = result["gait_speed"] / 100
    for column in ("stance_fraction", "swing_fraction", "double_support_fraction"):
        result[column] = result[column] / 100
    return result
