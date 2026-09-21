"""Fail-closed, discovery-first adapter for the Mendeley gait release."""
from __future__ import annotations

from pathlib import Path
import zipfile
import pandas as pd

from .external_schema import canonicalize, namespaced_key, source_files

_TABLE_SUFFIXES = {".csv", ".tsv", ".xlsx", ".xls", ".parquet"}


def _members(root: Path) -> list[str]:
    members = [str(path.relative_to(root)) for path in source_files(root)]
    for archive in root.rglob("*.zip"):
        try:
            with zipfile.ZipFile(archive) as handle:
                members.extend(f"{archive.name}!{name}" for name in handle.namelist())
        except (OSError, zipfile.BadZipFile):
            continue
    return sorted(set(members))


def discover_tables(root: Path) -> list[str]:
    """List candidate tables without opening participant-level data."""
    return [name for name in _members(root) if Path(name.split("!", 1)[-1]).suffix.lower() in _TABLE_SUFFIXES]


def audit(root: Path) -> dict:
    members = _members(root)
    lower = [name.lower() for name in members]
    return {"dataset": "mendeley_gait", "status": "OK" if members else "NOT_ESTIMABLE_SOURCE_COMPONENT_MISSING",
            "n_source_members": len(members), "candidate_tables": discover_tables(root),
            "has_raw_signal": any(any(token in n for token in ("imu", "acc", "gyro", "raw")) for n in lower),
            "has_pd": any("parkinson" in n or "pd" in n for n in lower),
            "has_control": any("control" in n or "healthy" in n for n in lower),
            "mapping_required": True, "source_members_are_not_published": True}


def collapse_bilateral(table: pd.DataFrame, participant: str, visit: str, side: str | None = None) -> pd.DataFrame:
    for key in (participant, visit):
        if key not in table:
            raise ValueError(f"bilateral collapse requires {key!r}")
    if side is not None and side not in table:
        raise ValueError(f"bilateral collapse requires {side!r}")
    keys = [participant, visit]
    numeric = [column for column in table.select_dtypes(include="number").columns if column not in keys]
    other = [column for column in table.columns if column not in numeric and column not in keys and column != side]
    grouped = table.groupby(keys, as_index=False)
    result = grouped[numeric].mean() if numeric else grouped.size().drop(columns="size")
    for column in other:
        result[column] = grouped[column].first()[column].to_numpy()
    result["source_record_count"] = grouped.size()["size"].to_numpy()
    return result


def to_canonical(table: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    if not mapping:
        raise ValueError("Mendeley requires an explicit reviewed column mapping")
    missing = set(mapping) - set(table.columns)
    if missing:
        raise ValueError(f"mapped source columns are absent: {sorted(missing)}")
    source = table.rename(columns=mapping).copy()
    required = {"participant_key", "visit_id"}
    if not required <= set(source):
        raise ValueError("exact participant and visit mappings are required")
    if source["participant_key"].isna().any() or source["visit_id"].isna().any():
        raise ValueError("participant and visit mappings cannot contain missing values")
    source["participant_key"] = source["participant_key"].map(lambda value: namespaced_key("mendeley", value))
    return canonicalize(source, "mendeley_gait")
