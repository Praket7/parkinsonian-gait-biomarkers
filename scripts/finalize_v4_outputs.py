#!/usr/bin/env python3
"""Write aggregate-only v4 closure tables from already frozen inference outputs."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import pandas as pd


def main():
    root=Path("results/v4/frozen"); primary=pd.read_csv(root/"primary_associations.csv")
    for name, features in {"variability_reliability.csv":["step_time_cv_longbout_v1","stride_time_cv_longbout_v1"],
                           "turning_features.csv":["turn_duration_v1","turn_step_count_v1","turn_step_duration_v1","peak_yaw_velocity_v1","turn_angle_per_step_v1"],
                           "harmonic_features.csv":["harmonic_ratio_ap_v1","stride_regularity_ap_v1"],
                           "reliability.csv":primary.feature.tolist(), "robustness.csv":primary.feature.tolist()}.items():
        rows=primary[primary.feature.isin(features)].copy()
        missing=sorted(set(features)-set(rows.feature))
        if missing: rows=pd.concat([rows,pd.DataFrame({"feature":missing,"status":"NOT_ESTIMABLE"})],ignore_index=True)
        if name in {"variability_reliability.csv","reliability.csv"}: rows["reliability_status"]="NOT_ESTIMABLE"; rows["estimability_reason"]="NO_REPEATED_V4_SESSION"
        if name=="robustness.csv": rows["task_transport"]="NOT_ESTIMABLE"; rows["site_transport"]="NOT_ESTIMABLE"
        rows.to_csv(root/name,index=False)
    files=[Path("configs/v4_analysis.yaml"),Path("configs/v4_feature_definitions.yaml"),Path("docs/v4_preregistration.md"),root/"protocol_manifest.json"]
    (root/"run_provenance.json").write_text(json.dumps({"schema":"v4-run-provenance-v1","row_level_data_published":False,"inputs_sha256":{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}},indent=2)+"\n")


if __name__ == "__main__": main()
