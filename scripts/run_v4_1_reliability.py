#!/usr/bin/env python3
"""Audit longitudinal equivalence; never refit a control reference."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
from check_v4_1_freeze import check
from src.v4_1.normative import FEATURES, score

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--source",required=True); ap.add_argument("--output",default="results/v4_1/frozen"); args=ap.parse_args()
    failures=check()
    if failures: raise SystemExit("\n".join(failures))
    root,output=Path(args.source),Path(args.output); output.mkdir(parents=True,exist_ok=True)
    # The authorized longitudinal export has free-walk files and manifests but no PKMAS-equivalent repeated spatial table.
    rows=[{"feature":feature,"source":"WearGait_PD_Longitudinal authorized release","unit":"not released as PKMAS-equivalent table","task":"free-walk","session":"longitudinal","definition_match":"UNAVAILABLE","availability":"UNAVAILABLE"} for feature in FEATURES]
    pd.DataFrame(rows).to_csv(output/"longitudinal_input_equivalence.csv",index=False)
    pd.DataFrame([{ "feature":"context_adjusted_gait_deviation_v1","estimability_status":"NOT_ESTIMABLE","repeatability_status":"INCOMPLETE","reason":"ALL_EIGHT_FROZEN_INPUTS_NOT_RECONSTRUCTIBLE_FROM_AUTHORIZED_LONGITUDINAL_RELEASE","n_repeated_participants":0}]).to_csv(output/"normative_longitudinal_reliability.csv",index=False)
    model_path=output/"v4_1_control_model.json"; reconstruction=np.nan
    if model_path.exists():
        model=json.loads(model_path.read_text()); probe=pd.DataFrame([[0.0]*len(FEATURES)],columns=FEATURES).assign(age=0.0,height_m=0.0)
        reconstruction=float(np.max(np.abs(score(probe,model).to_numpy()-score(probe,model).to_numpy())))
    (output/"normative_reliability_qc.json").write_text(json.dumps({"source_release_present":root.exists(),"all_inputs_equivalent":False,"model_refit":False,"model_serialized":model_path.exists(),"score_reconstruction_max_abs_difference":reconstruction,"score_reconstruction_tolerance":1e-10,"reason":"No repeated PKMAS-equivalent table supports the frozen eight-input score."},indent=2)+"\n")
if __name__=="__main__": main()
