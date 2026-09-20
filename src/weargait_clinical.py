"""Adapter for the two WearGait V1 clinical CSV exports.

The first CSV row is an explanatory row; the second row is the actual header.
Only fields with an unambiguous interpretation are exposed.
"""
from __future__ import annotations

from pathlib import Path
import re

import numpy as np
import pandas as pd


def _number(value):
    return pd.to_numeric(value, errors="coerce")


def _time_hours(value):
    parsed = pd.to_datetime(value, format="mixed", errors="coerce")
    return parsed.dt.hour + parsed.dt.minute / 60 + parsed.dt.second / 3600


def _yes_no(value):
    value = str(value).strip().lower()
    if value in {"yes", "y", "true", "1"}:
        return True
    if value in {"no", "n", "false", "0"}:
        return False
    return np.nan


def _part_iii_total(frame):
    """Sum scored Part III item columns, including both sides of bilateral items."""
    columns = [c for c in frame.columns if re.fullmatch(r"MDSUPDRS_3-(?:[0-9]+)(?:-[A-Za-z0-9]+)?", str(c))]
    values = frame[columns].apply(pd.to_numeric, errors="coerce")
    # A total is valid only when every scored item present in this export is present.
    return values.sum(axis=1, min_count=len(columns)).where(values.notna().all(axis=1))


def read_weargait_clinical(path, cohort=None):
    """Read one V1 PD/control table and return normalized participant rows."""
    frame = pd.read_csv(path, header=1, low_memory=False)
    id_col = next((c for c in frame if str(c).strip().lower() == "subject id"), None)
    if id_col is None:
        raise ValueError(f"clinical CSV has no Subject ID column: {path}")
    out = pd.DataFrame({"participant_id": frame[id_col].astype(str).str.strip()})
    out = out[out.participant_id.ne("nan") & out.participant_id.ne("")].copy()
    def col(*names):
        for name in names:
            if name in frame:
                return frame.loc[out.index, name]
        return pd.Series(np.nan, index=out.index)
    out["age"] = _number(col("Age (years)", "Age"))
    height = _number(col("Height (in)"))
    out["height_m"] = height * 0.0254
    out["sex"] = col("Sex", "Gender").astype("string").str.strip()
    out["disease_duration"] = _number(col("Years since PD diagnosis"))
    out["dbs_status"] = col("DBS?").map(_yes_no)
    session = _time_hours(col("Time of research session"))
    dose = _time_hours(col("Time of last medication dose"))
    delta = session - dose
    out["time_since_medication"] = delta.where(delta >= 0, delta + 24)
    out["mds_updrs_iii"] = _part_iii_total(frame).reindex(out.index)
    out["mds_updrs_gait_item"] = _number(col("MDSUPDRS_3-10"))
    out["clinical_cohort"] = cohort or ("control" if "controls" in Path(path).name.lower() else "pd")
    return out.reset_index(drop=True)


def load_v1_clinical(pd_path, controls_path=None):
    """Load PD and optional controls, retaining one row per participant ID."""
    tables = [read_weargait_clinical(pd_path, "pd")]
    if controls_path is not None:
        tables.append(read_weargait_clinical(controls_path, "control"))
    result = pd.concat(tables, ignore_index=True)
    return result.drop_duplicates("participant_id", keep="first")


def join_clinical_features(features, clinical):
    """Left-join normalized clinical fields by participant ID only."""
    if "participant_id" not in features or "participant_id" not in clinical:
        raise ValueError("both tables need participant_id")
    if clinical["participant_id"].duplicated().any():
        raise ValueError("clinical participant IDs must be unique before joining")
    columns = [c for c in clinical.columns if c != "participant_id"]
    return features.merge(clinical[["participant_id", *columns]], on="participant_id", how="left", validate="many_to_one")
