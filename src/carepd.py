"""Minimal reader and schema checks for the CARE-PD nested pickle release.

CARE-PD stores cohort pickles as ``participant -> trial -> fields``.  This
module extracts auditable trial metadata only; pose/translation arrays remain
available in the original record and are never silently converted to wearable
features.
"""

from pathlib import Path
import pickle
import re

import numpy as np
import pandas as pd


REQUIRED_FIELDS = {"pose", "trans", "fps", "UPDRS_GAIT", "medication", "other"}


def _cohort_name(path):
    # ``T-SDU-PD`` is a real cohort name; only release-processing suffixes go.
    return Path(path).stem.removesuffix("_canonical").removesuffix("_fixed")


def _trial_metadata(cohort, participant_id, trial_id, record, source_file):
    missing = REQUIRED_FIELDS - set(record)
    if missing:
        raise ValueError(f"{source_file}: {trial_id} missing fields {sorted(missing)}")
    pose, trans = np.asarray(record["pose"]), np.asarray(record["trans"])
    if pose.ndim != 2 or pose.shape[1] != 72:
        raise ValueError(f"{source_file}: {trial_id} pose must have shape (frames, 72), got {pose.shape}")
    if trans.ndim != 2 or trans.shape[1] != 3 or trans.shape[0] != pose.shape[0]:
        raise ValueError(f"{source_file}: {trial_id} trans must match pose frames, got {trans.shape}")
    fps = float(record["fps"])
    if not np.isfinite(fps) or fps <= 0:
        raise ValueError(f"{source_file}: {trial_id} fps must be positive")
    return {
        "dataset": "CARE-PD",
        "cohort": cohort,
        "participant_id": str(participant_id),
        "trial_id": str(trial_id),
        "source_file": str(source_file),
        "n_frames": int(pose.shape[0]),
        "fps": fps,
        "pose_shape": tuple(pose.shape),
        "trans_shape": tuple(trans.shape),
        "mds_updrs_gait_item": record["UPDRS_GAIT"],
        "medication_state": record["medication"],
        "other": record["other"],
    }


def read_carepd_pickle(path, *, validate=True):
    """Read one CARE-PD cohort pickle into raw records and trial metadata.

    Returns ``(raw, metadata)``.  ``raw`` is the unmodified nested mapping;
    ``metadata`` is a DataFrame with one row per trial.
    """
    path = Path(path)
    with path.open("rb") as stream:
        raw = pickle.load(stream)
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: expected participant mapping, got {type(raw).__name__}")
    rows = []
    for participant_id, trials in raw.items():
        if not isinstance(trials, dict):
            raise ValueError(f"{path}: participant {participant_id} is not a trial mapping")
        for trial_id, record in trials.items():
            if not isinstance(record, dict):
                raise ValueError(f"{path}: trial {trial_id} is not a record mapping")
            if validate:
                rows.append(_trial_metadata(_cohort_name(path), participant_id, trial_id, record, path))
            else:
                rows.append({"dataset": "CARE-PD", "cohort": _cohort_name(path),
                             "participant_id": str(participant_id), "trial_id": str(trial_id),
                             "source_file": str(path)})
    return raw, pd.DataFrame(rows)


def read_carepd_directory(directory, *, include_folds=False, validate=True):
    """Read top-level cohort pickles, optionally excluding fold definitions."""
    directory = Path(directory)
    paths = sorted(directory.glob("*.pkl"))
    if include_folds:
        paths += sorted((directory / "folds").rglob("*.pkl"))
    frames = []
    for path in paths:
        _, metadata = read_carepd_pickle(path, validate=validate)
        frames.append(metadata)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def infer_trial_context(trial_id):
    """Conservative labels from naming conventions; unknown stays unknown."""
    value = str(trial_id).lower()
    medication = next((x for x in ("on", "off") if re.search(rf"(?:^|[_-]){x}(?:$|[_-])", value)), None)
    return {"medication_from_id": medication, "walk_label": "walk" if "walk" in value else None}
