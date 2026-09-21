"""Fail-closed, discovery-first adapter for the Mendeley gait release."""
from __future__ import annotations

from pathlib import Path
import io
import re
import zipfile
import pandas as pd

from .external_schema import canonicalize, namespaced_key, source_files

_TABLE_SUFFIXES = {".csv", ".tsv", ".xlsx", ".xls", ".parquet"}
PROCESSED_COLUMNS = {"Mean stride amplitude (cm)": "stride_amplitude_cm", "SD stride amplitude (cm)": "stride_amplitude_sd_cm", "Mean stride speed (cm/s)": "gait_speed_m_s", "SD stride speed": "stride_speed_sd", "Mean speed correlation": "speed_correlation", "Mean height of foot lift (cm)": "foot_lift_cm", "SD height of foot lift (cm)": "foot_lift_sd_cm", "Arm swing indicator": "arm_swing_indicator", "Gait evaluation MDS-UPDRS": "gait_evaluation"}


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


def _processed_book(root: Path, number: int) -> pd.DataFrame:
    """Read only a declared processed workbook; raw IMU files are never joined."""
    archives = list(Path(root).rglob("*.zip"))
    for archive in archives:
        with zipfile.ZipFile(archive) as handle:
            member = next((n for n in handle.namelist() if re.search(fr"Tables in Excel/Table {number}\.xlsx$", n)), None)
            if member:
                return pd.read_excel(io.BytesIO(handle.read(member)), header=1)
    raise FileNotFoundError(f"Mendeley processed Table {number}.xlsx not found")


def parse_processed_id(value: object, table: int) -> dict:
    text = " ".join(str(value).replace("\xa0", " ").split())
    base = re.match(r"^(\d+)\s+([RL])", text, re.I)
    if not base:
        raise ValueError(f"unparseable processed-table ID: {text!r}")
    visit = 2 if table == 2 and "+ 6 months" in text.lower() else 1
    minutes = re.search(r"(\d+)\s*min", text, re.I)
    return {"processed_participant": f"{base.group(1)} {base.group(2).upper()}", "visit_order": visit,
            "time_since_medication_min": int(minutes.group(1)) if minutes else None}


def load_mendeley_processed_tables(root: Path) -> dict[str, pd.DataFrame]:
    tables = {}
    for number, label in ((1, "cross_sectional"), (2, "six_month"), (3, "medication_timing")):
        frame = _processed_book(root, number).rename(columns=PROCESSED_COLUMNS).dropna(subset=["ID"]).copy()
        parsed = frame["ID"].map(lambda x: parse_processed_id(x, number)).apply(pd.Series)
        frame = pd.concat([frame, parsed], axis=1)
        frame["participant_key"] = frame.processed_participant.map(lambda x: namespaced_key("mendeley_processed", x))
        frame["gait_speed_m_s"] = pd.to_numeric(frame.gait_speed_m_s, errors="coerce") / 100
        frame["gait_evaluation"] = pd.to_numeric(frame.gait_evaluation, errors="coerce")
        tables[label] = frame
    return tables
