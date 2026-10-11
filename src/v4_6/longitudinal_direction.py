"""Participant-paired long-interval deviation-direction inference for v4.6."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.v4_6.deviation_geometry import (
    conditional_residual,
    deviation_magnitude,
    precision_angle,
    precision_cosine,
    precision_matrix,
)

KEYS = ("participant", "session", "task")


def _validate(table: pd.DataFrame) -> pd.DataFrame:
    missing = [name for name in KEYS if name not in table]
    if missing:
        raise ValueError(f"missing longitudinal keys: {missing}")
    frame = table.copy()
    frame["session"] = frame["session"].astype(str)
    if frame.duplicated(list(KEYS)).any():
        raise ValueError("duplicate participant/session/task endpoint")
    return frame


def _paired_frames(table: pd.DataFrame, task: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    group = table.loc[table.task.eq(task)].copy()
    first = group.loc[group.session.eq("1")].set_index("participant")
    second = group.loc[group.session.eq("2")].set_index("participant")
    people = sorted(set(first.index) & set(second.index))
    return first.loc[people].copy(), second.loc[people].copy()


def pair_direction_rows(table: pd.DataFrame, model: dict, *, tasks: list[str] | tuple[str, ...]) -> pd.DataFrame:
    """Create one row per participant/task with scalar and directional paired change."""
    frame = _validate(table)
    precision = precision_matrix(model)
    records: list[dict] = []
    for task in tasks:
        first, second = _paired_frames(frame, task)
        if first.empty:
            continue
        r1 = conditional_residual(first, model)
        r2 = conditional_residual(second, model)
        for index, participant in enumerate(first.index):
            magnitude_1 = deviation_magnitude(r1[index], precision)
            magnitude_2 = deviation_magnitude(r2[index], precision)
            cosine = precision_cosine(r1[index], r2[index], precision)
            records.append({
                "participant": participant,
                "task": task,
                "score_session1": magnitude_1,
                "score_session2": magnitude_2,
                "score_change_s2_minus_s1": magnitude_2 - magnitude_1,
                "precision_cosine": cosine,
                "precision_angle_radians": precision_angle(r1[index], r2[index], precision),
                "direction_estimable": bool(np.isfinite(cosine)),
            })
    return pd.DataFrame.from_records(records)


def participant_bootstrap(values: np.ndarray, *, iterations: int, seed: int) -> np.ndarray:
    """Bootstrap participants and return median finite cosine for each resample."""
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        raise ValueError("no estimable participant directions")
    if iterations < 1:
        raise ValueError("iterations must be positive")
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(values), size=(iterations, len(values)))
    return np.median(values[indices], axis=1)


def permutation_null(table: pd.DataFrame, model: dict, *, task: str, iterations: int, seed: int) -> np.ndarray:
    """Permute session-2 participant assignments within one task."""
    frame = _validate(table)
    first, second = _paired_frames(frame, task)
    if first.empty:
        raise ValueError(f"no paired participants for {task}")
    precision = precision_matrix(model)
    r1 = conditional_residual(first, model)
    r2 = conditional_residual(second, model)
    rng = np.random.default_rng(seed)
    result = np.empty(iterations, dtype=float)
    for draw in range(iterations):
        permuted = r2[rng.permutation(len(r2))]
        values = np.asarray([precision_cosine(a, b, precision) for a, b in zip(r1, permuted)], dtype=float)
        finite = values[np.isfinite(values)]
        result[draw] = np.median(finite) if finite.size else np.nan
    return result


def plus_one_p_value(observed: float, null: np.ndarray) -> float:
    null = np.asarray(null, dtype=float)
    null = null[np.isfinite(null)]
    if not np.isfinite(observed) or null.size == 0:
        return float("nan")
    return float((1 + np.count_nonzero(null >= observed)) / (1 + len(null)))


def holm_adjust(p_values: dict[str, float]) -> dict[str, float]:
    """Holm family-wise adjustment, preserving the caller's keys."""
    finite = [(key, float(value)) for key, value in p_values.items() if np.isfinite(value)]
    finite.sort(key=lambda item: item[1])
    m = len(finite)
    adjusted: dict[str, float] = {key: float("nan") for key in p_values}
    running = 0.0
    for rank, (key, value) in enumerate(finite):
        candidate = min(1.0, (m - rank) * value)
        running = max(running, candidate)
        adjusted[key] = running
    return adjusted
