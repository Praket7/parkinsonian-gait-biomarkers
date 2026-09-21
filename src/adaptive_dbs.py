"""Fail-closed within-participant state adapter for adaptive DBS data."""
from __future__ import annotations

from pathlib import Path
import zipfile
import pandas as pd

from .external_schema import canonicalize, namespaced_key, source_files


def _members(root: Path) -> list[str]:
    members = [str(path.relative_to(root)) for path in source_files(root)]
    for archive in root.rglob("*.zip"):
        try:
            with zipfile.ZipFile(archive) as handle:
                members.extend(f"{archive.name}!{name}" for name in handle.namelist())
        except (OSError, zipfile.BadZipFile):
            continue
    return sorted(set(members))


def audit(root: Path) -> dict:
    members = _members(root)
    lower = [name.lower() for name in members]
    tables = [name for name in members if Path(name.split("!", 1)[-1]).suffix.lower() in {".csv", ".tsv", ".xlsx", ".xls", ".mat"}]
    return {"dataset": "adaptive_dbs", "status": "OK" if members else "NOT_ESTIMABLE_SOURCE_COMPONENT_MISSING",
            "n_source_members": len(members), "candidate_tables": tables,
            "has_state_metadata": any(any(token in name for token in ("state", "stim", "on_off", "onoff")) for name in lower),
            "has_gait_metadata": any(any(token in name for token in ("gait", "walk", "stride", "step")) for name in lower),
            "mapping_required": True, "source_members_are_not_published": True}


def paired_states(table: pd.DataFrame, feature: str, participant: str = "participant_key", state: str = "dbs_state", state_a: object | None = None, state_b: object | None = None) -> dict:
    """Summarize a pre-specified two-state within-participant contrast (B minus A)."""
    missing = {participant, state, feature} - set(table.columns)
    if missing:
        return {"feature": feature, "status": "NOT_ESTIMABLE", "reason": f"MISSING_COLUMNS:{','.join(sorted(missing))}", "n_participants": 0}
    frame = table[[participant, state, feature]].dropna()
    if not pd.api.types.is_numeric_dtype(frame[feature]):
        return {"feature": feature, "status": "NOT_ESTIMABLE", "reason": "FEATURE_NOT_NUMERIC", "n_participants": 0}
    states = list(pd.unique(frame[state]))
    if state_a is None and state_b is None:
        if len(states) != 2:
            return {"feature": feature, "status": "NOT_ESTIMABLE", "reason": "EXPECTED_EXACTLY_TWO_STATES", "n_participants": 0}
        state_a, state_b = sorted(states, key=lambda item: str(item))
    elif state_a is None or state_b is None or state_a == state_b:
        return {"feature": feature, "status": "NOT_ESTIMABLE", "reason": "INVALID_STATE_PAIR", "n_participants": 0}
    if state_a not in states or state_b not in states:
        return {"feature": feature, "status": "NOT_ESTIMABLE", "reason": "REQUESTED_STATE_NOT_PRESENT", "n_participants": 0}
    wide = frame[frame[state].isin([state_a, state_b])].pivot_table(index=participant, columns=state, values=feature, aggfunc="mean")
    if state_a not in wide or state_b not in wide:
        return {"feature": feature, "status": "NOT_ESTIMABLE", "reason": "MISSING_WITHIN_PARTICIPANT_STATE_PAIRS", "n_participants": 0}
    paired = wide[[state_a, state_b]].dropna()
    if len(paired) < 2:
        return {"feature": feature, "status": "NOT_ESTIMABLE", "reason": "MISSING_WITHIN_PARTICIPANT_STATE_PAIRS", "n_participants": int(len(paired))}
    contrast = paired[state_b] - paired[state_a]
    return {"feature": feature, "status": "OK", "n_participants": int(len(contrast)), "state_a": str(state_a), "state_b": str(state_b),
            "mean_paired_change": float(contrast.mean()), "median_paired_change": float(contrast.median())}


def to_canonical(table: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    if not mapping:
        raise ValueError("adaptive DBS requires an explicit reviewed column mapping")
    missing = set(mapping) - set(table.columns)
    if missing:
        raise ValueError(f"mapped source columns are absent: {sorted(missing)}")
    source = table.rename(columns=mapping).copy()
    if not {"participant_key", "visit_id", "dbs_state"} <= set(source):
        raise ValueError("DBS source requires explicit participant, visit, and state mappings")
    if source[["participant_key", "visit_id", "dbs_state"]].isna().any().any():
        raise ValueError("participant, visit, and DBS state mappings cannot contain missing values")
    source["participant_key"] = source["participant_key"].map(lambda value: namespaced_key("adaptive_dbs", value))
    return canonicalize(source, "adaptive_dbs")
