"""Small, aggregate-only CARE-PD translation analysis.

CARE-PD is a translation check, not an operational replication of walkway
features.  This module intentionally returns cohort-level summaries only.
"""
from __future__ import annotations

from pathlib import Path
import re
import warnings

import numpy as np
import pandas as pd
from scipy.stats import theilslopes

try:  # Keep deterministic speed sensitivities usable in minimal environments.
    import statsmodels.api as sm
except ImportError:  # pragma: no cover - exercised only without optional runtime deps
    sm = None

def _z(value):
    value = pd.to_numeric(value, errors="coerce")
    sd = value.std(ddof=0)
    return (value - value.mean()) / sd if np.isfinite(sd) and sd else value * np.nan


def _medication(value):
    text = str(value).strip().lower()
    match = re.search(r"\b(on|off)\b", text)
    return match.group(1) if match else None


def translation_speed_sensitivities(record, *, fps=None):
    """Return endpoint, robust framewise, and robust-slope z-speed summaries."""
    trans = np.asarray(record["trans"], dtype=float)
    rate = float(record.get("fps", fps))
    if trans.ndim != 2 or trans.shape[1] < 3 or len(trans) < 2 or not np.isfinite(rate) or rate <= 0:
        raise ValueError("trans must have at least two finite frames and positive fps")
    z = trans[:, 2]
    if not np.isfinite(z).all():
        raise ValueError("z translation contains non-finite values")
    dt = 1.0 / rate
    duration = (len(z) - 1) * dt
    endpoint = abs(z[-1] - z[0]) / duration
    framewise = float(np.median(np.abs(np.diff(z)) / dt))
    # Theil--Sen is quadratic.  A deterministic 100-frame sub-sample preserves
    # a robust trajectory sensitivity without making thousands of trials cubic
    # in wall-clock time.
    index = np.linspace(0, len(z) - 1, min(100, len(z))).round().astype(int)
    slope = float(abs(theilslopes(z[index], index * dt).slope))
    return {"endpoint_z_speed_m_s": float(endpoint),
            "framewise_z_speed_m_s": framewise,
            "slope_z_speed_m_s": slope,
            "duration_s": float(duration)}


def _speed_rows(raw, cohort):
    rows = []
    for participant, trials in raw.items():
        for trial, record in trials.items():
            try:
                speed = translation_speed_sensitivities(record)
            except (KeyError, TypeError, ValueError):
                continue
            severity = pd.to_numeric(pd.Series([record.get("UPDRS_GAIT")]), errors="coerce").iloc[0]
            rows.append({"cohort": cohort, "participant_key": f"{cohort}:{participant}",
                         "trial": str(trial), "severity": severity,
                         "medication": _medication(record.get("medication")), **speed})
    return pd.DataFrame(rows)


# The public CARE-PD canonical records currently contain pose (72 values) and
# root translation, not labelled foot/ankle trajectories or gait events.  Keep
# this allowlist deliberately small: deriving contacts from pose without the
# canonical body model would turn a schema audit into an unvalidated feature.
_TEMPORAL_KEYS = {
    # These are the prespecified matched-feature targets.  Canonical SMPL
    # records do not expose them; official H36M assets are required.
    "gait_speed": ("gait_speed",),
    "cadence": ("cadence", "cadence_steps_min"),
    "step_length_mean": ("step_length_mean",),
    "step_time_mean": ("step_time_mean",),
}


def _temporal_observations(raw, cohort):
    """Extract only explicitly supplied, QC-ready temporal observations.

    No pose/root-translation reconstruction is attempted.  A value must be a
    finite scalar or a finite sequence with at least three events; this keeps
    the matched layer honest when a release exposes no gait-event labels.
    """
    rows = []
    for participant, trials in raw.items():
        for trial, record in trials.items():
            for outcome, keys in _TEMPORAL_KEYS.items():
                key = next((name for name in keys if name in record), None)
                if key is None:
                    continue
                value = np.asarray(record[key], dtype=float)
                if value.ndim == 0:
                    value = value.reshape(1)
                value = value[np.isfinite(value)]
                if value.size < 3 or (value <= 0).any():
                    continue
                # Arrays represent event intervals; summarize deterministically.
                summary = float(np.mean(value)) if outcome == "stride_time_mean" else float(value[0])
                rows.append({"cohort": cohort, "participant_key": f"{cohort}:{participant}",
                             "trial": str(trial), "outcome": outcome, "value": summary})
    return pd.DataFrame(rows)


def matched_temporal_aggregate(table, *, min_participants=8):
    """Return aggregate matched CARE temporal results or explicit non-estimability.

    Event extraction is accepted only when canonical temporal observations are
    already present.  The current public schema normally has none, so the
    returned rows make that boundary visible instead of reporting fabricated
    cadence/stride associations.
    """
    outcomes = tuple(_TEMPORAL_KEYS)
    rows = []
    for cohort, raw in table.items():
        cohort = str(cohort)
        observations = _temporal_observations(raw, cohort)
        for outcome in outcomes:
            subset = observations[observations.outcome.eq(outcome)] if not observations.empty else observations
            participants = int(subset.participant_key.nunique()) if not subset.empty else 0
            if participants < min_participants:
                rows.append({"cohort": cohort, "outcome": outcome,
                             "n_trials": int(len(subset)), "n_participants": participants,
                             "effect": np.nan, "ci_low": np.nan, "ci_high": np.nan,
                             "p_value": np.nan, "status": "NOT_ESTIMABLE",
                             "estimability_reason": "official_h36m_assets_unavailable_or_prespecified_qc_insufficient"})
                continue
            fit_frame = subset.rename(columns={"value": outcome})
            result = _fit(fit_frame, outcome, min_participants=min_participants)
            result["status"] = result.get("status", "NOT_ESTIMABLE") if result.get("status") == "ok" else "NOT_ESTIMABLE"
            result["estimability_reason"] = "prespecified_event_qc_or_model_failed" if result["status"] != "ok" else "prespecified_event_qc_passed"
            rows.append({"cohort": cohort, "outcome": outcome, **result})
    return pd.DataFrame(rows, columns=["cohort", "outcome", "n_trials", "n_participants",
                                       "effect", "ci_low", "ci_high", "p_value", "status",
                                       "estimability_reason"])


def _fit(frame, outcome, *, min_participants=8):
    keep = frame[[outcome, "severity", "participant_key"]].dropna().copy()
    n_people = keep.participant_key.nunique()
    if sm is None:
        return {"n_trials": int(len(keep)), "n_participants": int(n_people),
                "effect": np.nan, "ci_low": np.nan, "ci_high": np.nan,
                "p_value": np.nan, "status": "statsmodels_unavailable"}
    if n_people < min_participants or keep.severity.nunique() < 3 or keep[outcome].nunique() < 3:
        return {"n_trials": int(len(keep)), "n_participants": int(n_people),
                "effect": np.nan, "ci_low": np.nan, "ci_high": np.nan,
                "p_value": np.nan, "status": "insufficient_data"}
    keep["outcome_z"], keep["severity_z"] = _z(keep[outcome]), _z(keep.severity)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fit = sm.GEE.from_formula("outcome_z ~ severity_z", groups="participant_key",
                                      data=keep, family=sm.families.Gaussian()).fit()
        ci = fit.conf_int().loc["severity_z"]
        return {"n_trials": int(len(keep)), "n_participants": int(n_people),
                "effect": float(fit.params["severity_z"]), "ci_low": float(ci.iloc[0]),
                "ci_high": float(ci.iloc[1]), "p_value": float(fit.pvalues["severity_z"]),
                "status": "ok"}
    except (ValueError, np.linalg.LinAlgError):
        return {"n_trials": int(len(keep)), "n_participants": int(n_people),
                "effect": np.nan, "ci_low": np.nan, "ci_high": np.nan,
                "p_value": np.nan, "status": "fit_failed"}


def safe_aggregate(table, *, min_participants=8):
    """Analyze an in-memory raw-record mapping and return identifier-free rows."""
    rows = []
    for cohort, raw in table.items():
        rows.extend(_speed_rows(raw, str(cohort)).to_dict("records"))
    data = pd.DataFrame(rows)
    if data.empty:
        return pd.DataFrame(columns=["cohort", "outcome", "n_trials", "n_participants",
                                     "effect", "ci_low", "ci_high", "p_value", "status"])
    output = []
    outcomes = ("endpoint_z_speed_m_s", "framewise_z_speed_m_s", "slope_z_speed_m_s")
    for cohort, cohort_data in data.groupby("cohort", sort=True):
        for outcome in outcomes:
            result = _fit(cohort_data, outcome, min_participants=min_participants)
            output.append({"cohort": cohort, "outcome": outcome, **result})
        if cohort == "BMCLab":
            state_data = cohort_data[cohort_data.medication.notna()]
            if state_data.medication.nunique() >= 2:
                for state, state_frame in state_data.groupby("medication", sort=True):
                    result = _fit(state_frame, "endpoint_z_speed_m_s", min_participants=min_participants)
                    output.append({"cohort": cohort, "outcome": f"endpoint_z_speed_m_s_{state}", **result})
    return pd.DataFrame(output)


def analyze_carepd_directory(directory, *, min_participants=8, cohorts=None):
    """Read authorized cohort pickles and return only aggregate summaries."""
    directory = Path(directory)
    output = {}
    allowed = set(cohorts) if cohorts else None
    for path in sorted(directory.glob("*.pkl")):
        cohort = path.stem.removesuffix("_canonical").removesuffix("_fixed")
        if allowed is not None and cohort not in allowed:
            continue
        with path.open("rb") as stream:
            import pickle
            raw = pickle.load(stream)
        if isinstance(raw, dict):
            output[cohort] = raw
    speed = safe_aggregate(output, min_participants=min_participants)
    temporal = matched_temporal_aggregate(output, min_participants=min_participants)
    return pd.concat([speed, temporal], ignore_index=True, sort=False)


if __name__ == "__main__":
    # ponytail: one aggregate smoke check; full cohort inference belongs to the authorized run.
    demo = {"BMCLab": {"p": {"t": {"trans": np.c_[np.zeros((20, 2)), np.arange(20) / 10],
                                      "fps": 10, "UPDRS_GAIT": 1, "medication": "off"}}}}
    assert translation_speed_sensitivities(next(iter(next(iter(demo.values())).values())).get("t"))['endpoint_z_speed_m_s'] == 1.0
