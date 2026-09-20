"""Auditable translation-only speed summary for canonical CARE-PD records.

This is intentionally not a gait-event or body-model feature extractor. It
uses endpoint displacement on the global translation axis with the greatest
absolute net displacement, divided by elapsed frame time.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from .carepd import read_carepd_pickle, REQUIRED_FIELDS


def _speed_row(cohort, participant_id, trial_id, record, source_file):
    missing = REQUIRED_FIELDS - set(record)
    if missing:
        raise ValueError(f"{source_file}: {trial_id} missing fields {sorted(missing)}")
    trans = np.asarray(record["trans"], dtype=float)
    if trans.ndim != 2 or trans.shape[1] != 3 or trans.shape[0] < 2:
        raise ValueError(f"{source_file}: {trial_id} trans must have shape (frames >= 2, 3), got {trans.shape}")
    fps = float(record["fps"])
    if not np.isfinite(fps) or fps <= 0:
        raise ValueError(f"{source_file}: {trial_id} fps must be positive")
    displacement = trans[-1] - trans[0]
    axis = int(np.argmax(np.abs(displacement)))
    duration = float((trans.shape[0] - 1) / fps)
    forward_displacement = float(abs(displacement[axis]))
    return {
        "dataset": "CARE-PD",
        "cohort": cohort,
        "participant_id": str(participant_id),
        "trial_id": str(trial_id),
        "source_file": str(source_file),
        "n_frames": int(trans.shape[0]),
        "fps": fps,
        "duration_s": duration,
        "speed_axis": axis,
        "forward_displacement_m": forward_displacement,
        "global_forward_speed_m_s": forward_displacement / duration,
        "mds_updrs_gait_item": record["UPDRS_GAIT"],
        "medication_state": record["medication"],
    }


def speed_from_pickle(path):
    """Return one translation-speed row per trial in one CARE-PD pickle."""
    path = Path(path)
    raw, _ = read_carepd_pickle(path, validate=False)
    cohort = path.stem.removesuffix("_canonical").removesuffix("_fixed")
    rows = []
    for participant_id, trials in raw.items():
        for trial_id, record in trials.items():
            rows.append(_speed_row(cohort, participant_id, trial_id, record, path))
    return pd.DataFrame(rows)


def speed_from_directory(directory):
    """Return translation-speed rows for top-level CARE-PD cohort pickles."""
    directory = Path(directory)
    frames = [speed_from_pickle(path) for path in sorted(directory.glob("*.pkl"))]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
