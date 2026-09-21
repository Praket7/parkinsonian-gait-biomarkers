"""Privacy-safe contracts shared by external participant-visit adapters."""
from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

CANONICAL_COLUMNS = ("dataset participant_key visit_id visit_order months_from_baseline site age sex height_m "
                     "disease_duration medication_state time_since_medication_min dbs_state "
                     "mds_updrs_gait_item mds_updrs_iii pigd_score gait_speed cadence step_length_mean "
                     "stride_length_mean step_time_mean stride_time_mean step_time_cv stride_time_cv source_record_count").split()
FORBIDDEN_PUBLIC_COLUMNS = {"participant_id", "subject_id", "recording_id", "session_id", "source_path", "email"}


def namespaced_key(dataset: str, source_id: object) -> str:
    """Create a deterministic source-local key; never join this across datasets."""
    return f"{dataset}:{hashlib.sha256(str(source_id).encode()).hexdigest()[:16]}"


def canonicalize(table: pd.DataFrame, dataset: str) -> pd.DataFrame:
    output = table.copy()
    output["dataset"] = dataset
    for column in CANONICAL_COLUMNS:
        if column not in output:
            output[column] = pd.NA
    output = output.loc[:, CANONICAL_COLUMNS]
    key = output[["participant_key", "visit_id"]].dropna()
    if key.duplicated().any():
        raise ValueError("duplicate participant-visit rows are not permitted")
    return output


def public_aggregate(table: pd.DataFrame) -> pd.DataFrame:
    """Reject identity-bearing columns before frozen outputs are written."""
    leaked = FORBIDDEN_PUBLIC_COLUMNS & set(table.columns)
    if leaked:
        raise ValueError(f"identity-bearing columns cannot be published: {sorted(leaked)}")
    return table


def source_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file() and not path.name.startswith("."))
