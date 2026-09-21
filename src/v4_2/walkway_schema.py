"""Schema-only audit of raw WearGait walkway streams."""
from __future__ import annotations
import csv
from pathlib import Path

REQUIRED=("Time","L Foot Contact","R Foot Contact","Walkway_X","Walkway_Y","WalkwayFoot")
def audit(root: Path) -> dict:
    paths=sorted(Path(root).rglob("*.csv")); sample=next((p for p in paths if "SelfPace" in p.name or "HurriedPace" in p.name),None)
    if sample is None: return {"status":"NOT_ESTIMABLE","reason":"NO_WALKWAY_CSV"}
    with sample.open(encoding="utf-8-sig",newline="") as handle: columns=next(csv.reader(handle))
    present={item:item in columns for item in REQUIRED}
    return {"status":"SCHEMA_AUDITED","n_csv_files":len(paths),"fields_present":present,
            "initial_contact":"DERIVABLE_FROM_CONTACT_RISING_EDGES" if present["L Foot Contact"] and present["R Foot Contact"] else "UNAVAILABLE",
            "foot_label":"WalkwayFoot" if present["WalkwayFoot"] else "UNAVAILABLE","time_unit":"seconds from Time header examples",
            "coordinate_fields":"pressure-grid strings, not documented calibrated rear-foot metric coordinates",
            "coordinate_compatibility":"UNAVAILABLE","sp_hp_separation":"filename task labels","repeated_sessions":"filename s1/s2 labels where present",
            "spatial_reconstruction_status":"NOT_ESTIMABLE_COORDINATE_CALIBRATION_UNAVAILABLE"}
