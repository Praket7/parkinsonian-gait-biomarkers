from pathlib import Path
import re
import pandas as pd

TASK_ALIASES = {
    "SelfPace": "SP", "HurriedPace": "HP", "SelfPace_mat": "SPm", "HurriedPace_mat": "HPm",
    "SelfPace_matTURN": "SPmT", "SelfPace_doorpat": "SPdoorpat",
    "HeadPosture": "HP", "HeadPosture_matTURN": "HPm", "TimedUpAndGo": "TUG",
    "FreeWalk": "FW", "TandemGait": "TG", "Balance": "B",
}
VALID_TASKS = {"SP", "HP", "SPm", "HPm", "SPmT", "TUG", "SPdoorpat", "FW", "TG", "B", *TASK_ALIASES}


def derive_site(participant_id):
    """Map known WearGait ID prefixes to the three documented sites."""
    value = str(participant_id)
    if value.startswith("NLS"):
        return "Johns_Hopkins_Outpatient"
    if value.startswith("HC"):
        return "Johns_Hopkins_Bayview"
    if value.startswith(("WPD", "WHC")):
        return "VA_Seattle"
    return "unknown"


def infer_task(path):
    stem = Path(path).stem
    for task in sorted(VALID_TASKS, key=len, reverse=True):
        if re.search(rf"(?:^|[_-]){re.escape(task)}(?:$|[_-])", stem):
            # Every caller needs the analysis label; returning raw aliases here
            # made filename filtering disagree with the later CSV normalizer.
            return canonical_task(task)
    return None


def canonical_task(value):
    value = str(value).strip()
    return TASK_ALIASES.get(value, value)


_ALIASES = {
    "participant": "participant_id", "subject_id": "participant_id", "subject": "participant_id",
    "visit": "session_id", "session": "session_id", "condition": "task",
    "updrs_iii": "mds_updrs_iii", "updrs3": "mds_updrs_iii",
    "updrs_gait": "mds_updrs_gait_item", "gait_item": "mds_updrs_gait_item",
    "speed": "gait_speed", "velocity": "gait_speed",
    "medication": "medication_state", "med_state": "medication_state",
    "time_since_med": "time_since_medication", "disease_duration_years": "disease_duration",
    "dbs": "dbs_status",
}


def _canonical_columns(frame):
    """Apply conservative aliases used by common de-identified exports."""
    rename = {c: _ALIASES[c.lower().strip()] for c in frame.columns if c.lower().strip() in _ALIASES}
    return frame.rename(columns=rename)


def load_csv_bouts(input_dir, file_glob="*.csv"):
    """Read raw CSVs without modifying them and attach auditable file metadata."""
    rows = []
    for path in sorted(Path(input_dir).rglob(file_glob)):
        frame = _canonical_columns(pd.read_csv(path))
        if "participant_id" not in frame:
            frame["participant_id"] = path.stem.split("_")[0]
        if "task" not in frame:
            frame["task"] = infer_task(path) or "unknown"
        frame["task"] = frame["task"].map(canonical_task)
        # Explicit metadata outranks an ID-derived fallback.
        if "site" not in frame:
            frame["site"] = frame["participant_id"].map(derive_site)
        frame["source_file"] = str(path)
        rows.append(frame)
    if not rows:
        return pd.DataFrame()
    result = pd.concat(rows, ignore_index=True)
    unknown = sorted(set(result["task"]) - VALID_TASKS)
    if unknown:
        raise ValueError(f"unknown task names: {unknown}")
    return result
