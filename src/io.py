from pathlib import Path
import re
import pandas as pd

VALID_TASKS = {"SP", "HP", "SPm", "HPm", "SPmT", "TUG", "SPdoorpat", "FW", "TG", "B"}


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
            return task
    return None


def load_csv_bouts(input_dir, file_glob="*.csv"):
    """Read raw CSVs without modifying them and attach auditable file metadata."""
    rows = []
    for path in sorted(Path(input_dir).glob(file_glob)):
        frame = pd.read_csv(path)
        if "participant_id" not in frame:
            frame["participant_id"] = path.stem.split("_")[0]
        if "task" not in frame:
            frame["task"] = infer_task(path) or "unknown"
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
