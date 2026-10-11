"""Healthy-reference participant bootstrap for v4.6 longitudinal sensitivity."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.v4_1.normative import fit_reference
from src.v4_6.longitudinal_direction import pair_direction_rows
from src.v4_6.score_agreement import icc_a1


def resample_controls_by_participant(controls: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Resample control participants as clusters and give duplicate draws unique IDs."""
    if "participant_id" not in controls:
        raise ValueError("controls require participant_id")
    people = controls.participant_id.dropna().unique()
    if len(people) == 0:
        raise ValueError("controls are empty")
    chosen = rng.choice(people, size=len(people), replace=True)
    blocks = []
    for draw, participant in enumerate(chosen):
        block = controls.loc[controls.participant_id.eq(participant)].copy()
        block["participant_id"] = f"control_boot_{draw}"
        blocks.append(block)
    return pd.concat(blocks, ignore_index=True)


def reference_bootstrap(
    controls: pd.DataFrame,
    endpoints: pd.DataFrame,
    features: list[str] | tuple[str, ...],
    *,
    iterations: int,
    seed: int,
    covariance_method: str = "sample",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Propagate healthy-reference sampling uncertainty through paired long-interval endpoints.

    The same fitted reference is used for both visits within each resample. Percentiles
    across resamples therefore quantify reference-estimation sensitivity, not participant
    sampling confidence intervals.
    """
    if iterations < 1:
        raise ValueError("iterations must be positive")
    if controls.empty or "clinical_cohort" not in controls:
        raise ValueError("reference fitting accepts controls only")
    if controls.clinical_cohort.astype(str).str.lower().ne("control").any():
        raise ValueError("reference fitting accepts controls only")
    required = {"participant", "session", "task", "age", "height_m", *features}
    missing = required - set(endpoints.columns)
    if missing:
        raise ValueError(f"missing longitudinal columns: {sorted(missing)}")
    frame = endpoints.copy()
    frame["session"] = frame.session.astype(str)
    if frame.duplicated(["participant", "session", "task"]).any():
        raise ValueError("duplicate participant/session/task endpoint")
    tasks = sorted(frame.task.dropna().unique())
    rng = np.random.default_rng(seed)
    aggregate: list[dict] = []
    participant_rows: list[dict] = []
    for resample in range(1, iterations + 1):
        sampled = resample_controls_by_participant(controls, rng)
        model = fit_reference(sampled, features=list(features), covariance_method=covariance_method)
        pairs = pair_direction_rows(frame, model, tasks=tasks)
        for task, group in pairs.groupby("task", sort=True):
            first = group.score_session1.to_numpy(float)
            second = group.score_session2.to_numpy(float)
            finite_direction = group.precision_cosine[np.isfinite(group.precision_cosine)].to_numpy(float)
            aggregate.append({
                "resample": resample,
                "task": task,
                "n_paired": int(len(group)),
                "icc_a1": icc_a1(first, second) if len(group) >= 2 else float("nan"),
                "median_precision_cosine": float(np.median(finite_direction)) if len(finite_direction) else float("nan"),
                "mean_score_change": float(group.score_change_s2_minus_s1.mean()),
                "median_score_change": float(group.score_change_s2_minus_s1.median()),
                "uncertainty_type": "healthy_reference_estimation",
            })
            for row in group.itertuples(index=False):
                participant_rows.append({
                    "resample": resample,
                    "task": task,
                    "participant": row.participant,
                    "score_change_s2_minus_s1": row.score_change_s2_minus_s1,
                    "precision_cosine": row.precision_cosine,
                    "uncertainty_type": "healthy_reference_estimation",
                })
    return pd.DataFrame(aggregate), pd.DataFrame(participant_rows)


def summarize_reference_uncertainty(table: pd.DataFrame) -> pd.DataFrame:
    """Aggregate reference-bootstrap distributions without calling them confidence intervals."""
    rows = []
    for task, group in table.groupby("task", sort=True):
        row = {"task": task, "resamples": int(group.resample.nunique()), "uncertainty_type": "healthy_reference_estimation"}
        for metric in ("icc_a1", "median_precision_cosine", "mean_score_change", "median_score_change"):
            values = pd.to_numeric(group[metric], errors="coerce").dropna().to_numpy(float)
            row[f"{metric}_median"] = float(np.median(values)) if len(values) else float("nan")
            if len(values):
                row[f"{metric}_reference_p025"] = float(np.quantile(values, 0.025))
                row[f"{metric}_reference_p975"] = float(np.quantile(values, 0.975))
            else:
                row[f"{metric}_reference_p025"] = row[f"{metric}_reference_p975"] = float("nan")
        rows.append(row)
    return pd.DataFrame(rows)
