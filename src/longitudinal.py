"""Small, task-specific helpers for two-session longitudinal reliability."""
from __future__ import annotations

import numpy as np
import pandas as pd


def prepare_two_session_reliability(
    frame: pd.DataFrame,
    feature_columns: list[str],
    *,
    participant_column: str = "participant_id",
    session_column: str = "session",
    task_column: str = "task",
) -> pd.DataFrame:
    """Return complete, task-specific participant rows with exactly two sessions."""
    required = {participant_column, session_column, task_column, *feature_columns}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    work = frame[[participant_column, session_column, task_column, *feature_columns]].copy()
    work = work.dropna(subset=[participant_column, session_column, task_column])
    # Multiple bouts within a session are reduced before reliability is formed.
    work = work.groupby([participant_column, task_column, session_column], as_index=False)[feature_columns].mean()
    counts = work.groupby([participant_column, task_column])[session_column].nunique()
    eligible = counts[counts == 2].index
    work = work.set_index([participant_column, task_column])
    work = work.loc[work.index.isin(eligible)].reset_index()
    work = work.sort_values([participant_column, task_column, session_column])
    rows = []
    for (participant, task), group in work.groupby([participant_column, task_column], sort=False):
        if len(group) != 2 or group[session_column].nunique() != 2:
            continue
        first, second = group.iloc[0], group.iloc[1]
        row = {participant_column: participant, task_column: task, "session_1": first[session_column], "session_2": second[session_column]}
        for feature in feature_columns:
            row[f"{feature}_session_1"] = first[feature]
            row[f"{feature}_session_2"] = second[feature]
        rows.append(row)
    return pd.DataFrame(rows)


def reliability_qc(table: pd.DataFrame, feature_columns: list[str]) -> dict[str, int]:
    """Summarize the prepared table without exposing any participant identifiers."""
    expected = len(feature_columns) * 2
    complete = int(table[[f"{feature}_session_{i}" for feature in feature_columns for i in (1, 2)]].notna().all(axis=1).sum()) if not table.empty else 0
    return {"rows": int(len(table)), "features": len(feature_columns), "complete_feature_rows": complete, "expected_value_columns": expected}


def icc_2_1(values: np.ndarray | list[list[float]]) -> float:
    """Two-way random-effects, absolute-agreement, single-measure ICC(2,1)."""
    matrix = np.asarray(values, dtype=float)
    if matrix.ndim != 2 or matrix.shape[1] != 2 or matrix.shape[0] < 2 or not np.isfinite(matrix).all():
        raise ValueError("values must be a finite n-by-2 matrix with n >= 2")
    n, k = matrix.shape
    grand = matrix.mean()
    ms_rows = k * np.square(matrix.mean(axis=1) - grand).sum() / (n - 1)
    ms_columns = n * np.square(matrix.mean(axis=0) - grand).sum() / (k - 1)
    ms_error = np.square(matrix - matrix.mean(axis=1, keepdims=True) - matrix.mean(axis=0) + grand).sum() / ((n - 1) * (k - 1))
    denominator = ms_rows + (k - 1) * ms_error + k * (ms_columns - ms_error) / n
    return float((ms_rows - ms_error) / denominator) if denominator else float("nan")
