"""Reconstruct the frozen gait inputs from documented WearGait walkway cells."""
from __future__ import annotations

import numpy as np
import pandas as pd

CELL_PITCH_CM = 1.27
FEATURES = (
    "gait_speed", "cadence", "step_length_mean", "stride_length_mean",
    "step_time_mean", "stride_time_mean", "step_time_cv", "stride_time_cv",
)


def _time(value: object) -> float:
    return float(str(value).replace(" sec", ""))


def _vector(value: object) -> np.ndarray:
    return np.fromstring(str(value).replace("|", " "), sep=" ")


def initial_footfalls(table: pd.DataFrame) -> pd.DataFrame:
    """Return one documented X/Y centroid per valid foot initial contact.

    The supplied Figure S5 defines X as the walkway's longitudinal axis.  The
    cell coordinates are converted with the published 1.27-cm cell pitch.
    """
    required = {"Time", "GeneralEvent", "L Foot Contact", "R Foot Contact", "Walkway_X", "Walkway_Y", "WalkwayFoot"}
    missing = required.difference(table.columns)
    if missing:
        raise ValueError(f"missing walkway columns: {sorted(missing)}")
    event = table["GeneralEvent"].fillna("").astype(str).eq("Walk")
    segment = (event & ~event.shift(fill_value=False)).cumsum()
    rows: list[dict] = []
    for foot, contact_column in (("L", "L Foot Contact"), ("R", "R Foot Contact")):
        contact = pd.to_numeric(table[contact_column], errors="coerce").fillna(0).gt(0)
        starts = np.flatnonzero(contact.to_numpy() & ~contact.shift(fill_value=False).to_numpy())
        for index in starts:
            if not event.iloc[index]:
                continue
            labels = str(table.iloc[index]["WalkwayFoot"]).split("|")
            x, y = _vector(table.iloc[index]["Walkway_X"]), _vector(table.iloc[index]["Walkway_Y"])
            if len(labels) != len(x) or len(x) != len(y):
                continue
            mask = np.asarray(labels, dtype=object) == foot
            if not mask.any():
                continue
            rows.append({
                "time": _time(table.iloc[index]["Time"]), "foot": foot,
                "pass": int(segment.iloc[index]),
                "x_cm": float(x[mask].mean() * CELL_PITCH_CM),
                "y_cm": float(y[mask].mean() * CELL_PITCH_CM),
            })
    result = pd.DataFrame(rows, columns=("time", "foot", "pass", "x_cm", "y_cm"))
    if result.empty:
        raise ValueError("no valid walking initial contacts")
    result = result.sort_values("time").reset_index(drop=True)
    if result.time.duplicated().any() or result.time.diff().dropna().le(0).any():
        raise ValueError("non-monotonic initial contacts")
    return result


def summarize_footfalls(events: pd.DataFrame) -> dict[str, float]:
    """Compute all eight frozen inputs from footfall centroids and contact time."""
    step_time: list[float] = []
    stride_time: list[float] = []
    step_length: list[float] = []
    stride_length: list[float] = []
    distance_cm = 0.0
    ambulation_time = 0.0
    for _, passage in events.groupby("pass", sort=True):
        passage = passage.sort_values("time").reset_index(drop=True)
        if len(passage) < 4 or not passage.foot.ne(passage.foot.shift()).iloc[1:].all():
            raise ValueError("invalid or insufficient alternating contacts in a walking pass")
        step_time.extend(np.diff(passage.time).tolist())
        step_length.extend(np.abs(np.diff(passage.x_cm)).tolist())
        for foot in ("L", "R"):
            same_foot = passage.loc[passage.foot.eq(foot)]
            if len(same_foot) >= 2:
                stride_time.extend(np.diff(same_foot.time).tolist())
                stride_length.extend(np.abs(np.diff(same_foot.x_cm)).tolist())
        ambulation_time += float(passage.time.iloc[-1] - passage.time.iloc[0])
        distance_cm += float(abs(passage.x_cm.iloc[-1] - passage.x_cm.iloc[0]))
    step_time_array, stride_time_array = np.asarray(step_time), np.asarray(stride_time)
    if len(step_time_array) < 3 or len(stride_time_array) < 3 or ambulation_time <= 0:
        raise ValueError("insufficient valid intervals")
    return {
        "gait_speed": float(distance_cm / ambulation_time),
        "cadence": float(60 * len(step_time_array) / ambulation_time),
        "step_length_mean": float(np.mean(step_length)),
        "stride_length_mean": float(np.mean(stride_length)),
        "step_time_mean": float(np.mean(step_time_array)),
        "stride_time_mean": float(np.mean(stride_time_array)),
        "step_time_cv": float(100 * np.std(step_time_array, ddof=1) / np.mean(step_time_array)),
        "stride_time_cv": float(100 * np.std(stride_time_array, ddof=1) / np.mean(stride_time_array)),
    }


def reconstruct_csv(path: str) -> dict[str, float]:
    columns = ["Time", "GeneralEvent", "L Foot Contact", "R Foot Contact", "Walkway_X", "Walkway_Y", "WalkwayFoot"]
    return summarize_footfalls(initial_footfalls(pd.read_csv(path, usecols=columns, low_memory=False)))


def reconstruct_passes_csv(path: str) -> pd.DataFrame:
    """Return independently reconstructed valid walkway passes from one CSV.

    This deliberately does not pool passes.  A caller may define a new
    multi-pass protocol endpoint, while the original file-level reconstruction
    remains unchanged for the frozen v4.3 endpoint.
    """
    columns = ["Time", "GeneralEvent", "L Foot Contact", "R Foot Contact", "Walkway_X", "Walkway_Y", "WalkwayFoot"]
    events = initial_footfalls(pd.read_csv(path, usecols=columns, low_memory=False))
    rows: list[dict[str, float | int]] = []
    for passage, group in events.groupby("pass", sort=True):
        try:
            rows.append({"pass": int(passage), **summarize_footfalls(group)})
        except ValueError:
            continue
    result = pd.DataFrame(rows)
    if result.empty:
        raise ValueError("no valid independently reconstructed walking passes")
    return result
