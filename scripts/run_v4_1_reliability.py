#!/usr/bin/env python3
"""Audit longitudinal equivalence; never refit a control reference."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd
from check_v4_1_freeze import check
from src.v4_1.normative import FEATURES

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--source",required=True); ap.add_argument("--output",default="results/v4_1/frozen"); args=ap.parse_args()
    failures=check()
    if failures: raise SystemExit("\n".join(failures))
    root,output=Path(args.source),Path(args.output); output.mkdir(parents=True,exist_ok=True)
    # The authorized longitudinal export has free-walk files and manifests but no PKMAS-equivalent repeated spatial table.
    rows=[{"feature":feature,"source":"WearGait_PD_Longitudinal authorized release","unit":"not released as PKMAS-equivalent table","task":"free-walk","session":"longitudinal","definition_match":"UNAVAILABLE","availability":"UNAVAILABLE"} for feature in FEATURES]
    pd.DataFrame(rows).to_csv(output/"longitudinal_input_equivalence.csv",index=False)
    pd.DataFrame([{ "feature":"context_adjusted_gait_deviation_v1","estimability_status":"NOT_ESTIMABLE","repeatability_status":"INCOMPLETE","reason":"ALL_EIGHT_FROZEN_INPUTS_NOT_RECONSTRUCTIBLE_FROM_AUTHORIZED_LONGITUDINAL_RELEASE","n_repeated_participants":0}]).to_csv(output/"normative_longitudinal_reliability.csv",index=False)
    (output/"normative_reliability_qc.json").write_text(json.dumps({"source_release_present":root.exists(),"all_inputs_equivalent":False,"model_refit":False,"score_reconstruction_checked":False,"reason":"No repeated PKMAS-equivalent table supports the frozen eight-input score."},indent=2)+"\n")
if __name__=="__main__": main()
