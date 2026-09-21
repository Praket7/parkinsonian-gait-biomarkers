"""Schema-first adapter for the Mobilise-D CVS public release."""
from __future__ import annotations

import csv
import io
from pathlib import Path
import re
import zipfile

import pandas as pd

from .external_schema import canonicalize, namespaced_key

_VISIT_COLUMNS = ("visit_number", "visit", "visit_id", "visitid")
_ID_COLUMNS = ("participantid", "participant_id", "participant", "subject_id")
_DMO_MAP = {"averagestridespeed": "gait_speed", "averagewalkingspeed": "gait_speed",
            "averagestridelength": "stride_length_mean", "averagecadence": "cadence",
            "averagestrideduration": "stride_time_mean"}


def _norm(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())


def _members(root: Path) -> list[str]:
    names: list[str] = []
    if not root.exists():
        return names
    for archive in root.rglob("*.zip"):
        try:
            with zipfile.ZipFile(archive) as handle:
                names.extend(f"{archive.name}!{name}" for name in handle.namelist())
        except (OSError, zipfile.BadZipFile):
            continue
    names.extend(str(path.relative_to(root)) for path in root.rglob("*") if path.is_file())
    return sorted(set(names))


def _headers(root: Path) -> dict[str, list[str]]:
    """Read CSV headers from extracted files and archives, never participant rows."""
    found: dict[str, list[str]] = {}
    if not root.exists():
        return found
    for path in sorted(root.rglob("*")):
        try:
            if path.is_file() and path.suffix.lower() == ".csv":
                with path.open("r", encoding="utf-8-sig", newline="") as handle:
                    found[str(path.relative_to(root))] = next(csv.reader(handle))
            elif path.is_file() and path.suffix.lower() == ".zip":
                with zipfile.ZipFile(path) as archive:
                    for member in archive.infolist():
                        if member.is_dir() or not member.filename.lower().endswith(".csv"):
                            continue
                        with io.TextIOWrapper(archive.open(member), encoding="utf-8-sig", newline="") as handle:
                            found[f"{path.name}!{member.filename}"] = next(csv.reader(handle))
        except (OSError, UnicodeError, StopIteration, zipfile.BadZipFile):
            continue
    return found


def _schema_flags(headers: dict[str, list[str]]) -> dict[str, object]:
    columns = [column for values in headers.values() for column in values]
    keys = {_norm(column) for column in columns}
    return {
        "participant_identifier_fields": sorted({c for c in columns if _norm(c) in {_norm(x) for x in _ID_COLUMNS}}),
        "visit_fields": sorted({c for c in columns if _norm(c) in {_norm(x) for x in _VISIT_COLUMNS}}),
        "exact_mds_updrs_3_10": any(_norm(c) in {"mdsupdrs310", "mdsupdrs3_10"} for c in columns),
        "part_iii_or_pigd_fields": sorted(c for c in columns if "updrs" in str(c).lower() or "pigd" in str(c).lower()),
        "medication_fields": sorted(c for c in columns if any(x in _norm(c) for x in ("medication", "levodopa", "onoff", "lastdose"))),
        "dmo_fields": sorted(c for c in columns if _norm(c) in _DMO_MAP or "stride" in _norm(c) or "cadence" in _norm(c)),
        "site_fields": sorted(c for c in columns if any(x in _norm(c) for x in ("site", "country", "center"))),
    }


def audit(root: Path) -> dict:
    """Perform the required schema gate without loading source observations."""
    root = Path(root)
    members, headers = _members(root), _headers(root)
    lower = [name.lower() for name in members]
    pd_candidates = [name for name in members if "pd_dataset" in name.lower()]
    components = {
        # Raw signals and non-PD cohorts are useful extensions, but the CVS
        # public analysis release is sufficient for this project's prespecified
        # aggregate-DMO PD analysis.  Do not block that analysis merely because
        # optional components were not released alongside it.
        "raw_arm_foot_imu_optional": any(any(x in name for x in ("imu", "acceler", "gyro")) for name in lower),
        "pd_participant_files": bool(pd_candidates) or any("parkinson" in name or re.search(r"(^|[^a-z])pd([^a-z]|$)", name) for name in lower),
        "control_files_optional": any("control" in name or "healthy" in name for name in lower),
        "cross_sectional_gait_table": any(x in name for name in lower for x in ("gait", "walk", "dmo")) and bool(headers),
        "six_month_repeated_assessment_table": any(x in name for name in lower for x in ("6month", "six_month", "t2", "t3")),
        "medication_timing_table": any("medication" in name or "timing" in name for name in lower),
    }
    required = ("pd_participant_files", "cross_sectional_gait_table", "six_month_repeated_assessment_table", "medication_timing_table")
    missing = [name for name in required if not components[name]]
    return {"dataset": "mobilised_cvs", "status": "OK" if members and not missing else "NOT_ESTIMABLE_SOURCE_COMPONENT_MISSING",
            "reason": None if members and not missing else "REQUIRED_RELEASE_COMPONENTS_NOT_CONFIRMED",
            "n_source_members": len(members), "csv_headers": headers,
            "pd_dataset_present": bool(pd_candidates), "pd_dataset_candidates": pd_candidates,
            "components": components, "missing_components": missing, "schema": _schema_flags(headers),
            "participant_visit_key_unique": "REQUIRES_ROW_AUDIT",
            "data_dictionary_entries": [name for name in members if "dictionary" in name.lower()],
            "source_members_are_not_published": True}


def resolve_anchor(columns: list[str]) -> tuple[str | None, str]:
    """Resolve exact 3.10, then explicit construct, then broad Part III."""
    normalized = {_norm(column): column for column in columns}
    for key in ("mdsupdrs310", "mdsupdrs3_10"):
        if key in normalized:
            return normalized[key], "exact"
    for key, original in normalized.items():
        if "pigd" in key or "gaitposture" in key:
            return original, "construct_level"
    for key, original in normalized.items():
        if "updrs" in key and ("iii" in key or "part3" in key or key.endswith("3")):
            return original, "broad_motor"
    return None, "ANCHOR_UNAVAILABLE"


def convert_units(values: pd.Series, source_unit: str, target_unit: str) -> pd.Series:
    factors = {("km/h", "m/s"): 1 / 3.6, ("cm", "m"): .01, ("mm", "m"): .001,
               ("ms", "s"): .001, ("steps/hour", "steps/min"): 1 / 60}
    source, target = source_unit.lower().strip(), target_unit.lower().strip()
    if source == target:
        return pd.to_numeric(values, errors="coerce")
    if (source, target) not in factors:
        raise ValueError(f"unsupported Mobilise-D unit conversion: {source_unit} -> {target_unit}")
    return pd.to_numeric(values, errors="coerce") * factors[(source, target)]


def to_canonical(table: pd.DataFrame, mapping: dict[str, str], *, units: dict[str, tuple[str, str]] | None = None) -> pd.DataFrame:
    source = table.rename(columns=mapping).copy()
    if "participant_key" not in source or "visit_id" not in source:
        raise ValueError("Mobilise-D requires explicit participant and visit mappings")
    if "visit_order" not in source:
        raise ValueError("Mobilise-D requires a source-defined visit_order mapping")
    for column, (source_unit, target_unit) in (units or {}).items():
        if column in source:
            source[column] = convert_units(source[column], source_unit, target_unit)
    source["participant_key"] = source["participant_key"].map(lambda value: namespaced_key("mobilised_cvs", value))
    return canonicalize(source, "mobilised_cvs")


def reliable_week(table: pd.DataFrame) -> pd.Series:
    if "reliable_week_status" not in table:
        return pd.Series(False, index=table.index)
    return table.reliable_week_status.astype(str).str.upper().eq("PASS")


def filter_reliable_week(table: pd.DataFrame, *, sensitivity: bool = False) -> pd.DataFrame:
    return table.copy() if sensitivity else table.loc[reliable_week(table)].copy()
