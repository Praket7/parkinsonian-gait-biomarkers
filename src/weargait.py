"""Small adapter for WearGait signal CSV exports.

The public export also contains MATLAB timetable files.  Those are not
silently coerced here: scipy exposes them as opaque MATLAB objects, while the
CSV exports provide explicit contact timestamps suitable for the existing
feature API.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from .features import extract_bout_features
from .io import canonical_task, derive_site, infer_task

_TIME_RE = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")


def _seconds(values) -> np.ndarray:
    """Parse WearGait's ``0.01 sec`` strings without assuming row rate."""
    if pd.api.types.is_numeric_dtype(values):
        return pd.to_numeric(values, errors="coerce").to_numpy(float)
    return np.asarray([
        float(m.group(0)) if (m := _TIME_RE.search(str(value))) else np.nan
        for value in values
    ])


def _rising_edges(values, times) -> np.ndarray:
    signal = pd.to_numeric(values, errors="coerce").fillna(0).to_numpy(float)
    valid = np.isfinite(times)
    high = signal > 0
    starts = high & ~np.r_[False, high[:-1]]
    return times[starts & valid]


def _paired_longest_bout(left: np.ndarray, right: np.ndarray, max_gap: float = 2.0):
    """Select one shared segment so left/right features cannot cross a stop."""
    all_times = np.sort(np.r_[left, right])
    if len(all_times) < 2:
        return left, right
    breaks = np.flatnonzero(np.diff(all_times) > max_gap) + 1
    segment = max(np.split(all_times, breaks), key=len)
    lo, hi = segment[0], segment[-1]
    return left[(left >= lo) & (left <= hi)], right[(right >= lo) & (right <= hi)]


def _participant_session(path: Path) -> tuple[str, str]:
    # Control exports use e.g. ``NLS193 (control)_SelfPace`` rather than an
    # underscore immediately after the ID.
    match = re.match(r"(?P<participant>[A-Za-z]+\d+)(?P<session>s\d+)?", path.stem)
    if not match:
        return path.stem, "v1"
    return match.group("participant"), match.group("session") or "v1"


def read_weargait_csv(path) -> dict:
    """Read one contact-signal CSV and derive one auditable bout row."""
    path = Path(path)
    header = pd.read_csv(path, nrows=0)
    needed = {"Time", "L Foot Contact", "R Foot Contact"}
    if not needed.issubset(header.columns):
        raise ValueError(f"not a WearGait contact CSV: {path}")
    usecols = sorted(needed | ({"GeneralEvent"} if "GeneralEvent" in header.columns else set()))
    frame = pd.read_csv(path, usecols=usecols, low_memory=False)
    times = _seconds(frame["Time"])
    # The release explicitly annotates walking.  Do not let contact changes in
    # standing/turning inflate a straight-walk temporal summary.
    if "GeneralEvent" in frame:
        walking = frame["GeneralEvent"].astype(str).str.strip().str.lower().eq("walk").to_numpy()
        if walking.any():
            frame, times = frame.loc[walking].reset_index(drop=True), times[walking]
    participant, session = _participant_session(path)
    task = canonical_task(infer_task(path) or "unknown")
    left, right = _paired_longest_bout(
        _rising_edges(frame["L Foot Contact"], times),
        _rising_edges(frame["R Foot Contact"], times),
    )
    features = extract_bout_features({"left_contacts": left, "right_contacts": right})
    return {
        "participant_id": participant,
        "session_id": session,
        "site": derive_site(participant),
        "task": task,
        "source_file": str(path),
        "source_format": "weargait_csv_signal",
        **features,
    }


def load_weargait_csv_bouts(input_dir, file_glob="*.csv") -> pd.DataFrame:
    """Load only explicit WearGait contact CSVs; ignore manifests/clinical CSVs."""
    rows = []
    for path in sorted(Path(input_dir).rglob(file_glob)):
        try:
            rows.append(read_weargait_csv(path))
        except ValueError as exc:
            if "not a WearGait contact CSV" not in str(exc):
                raise
    return pd.DataFrame(rows)
