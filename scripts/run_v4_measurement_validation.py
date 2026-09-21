#!/usr/bin/env python3
"""Outcome-blind v4 contact/sensor extraction and convergence validation."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
import yaml
from src.weargait import _rising_edges, _seconds, _participant_session
from src.io import canonical_task, derive_site, infer_task
from src.v4.variability_rescue import convergence_errors, choose_minimum_cycles, longbout_variability
from src.v4.arm_swing import arm_features
from src.v4.axial_control import axial_rotation_smoothness
from src.v4.harmonic_features import harmonic_ratio, stride_regularity
from src.v4.turning import turning_features


def _walk(frame):
    return frame[frame.GeneralEvent.astype(str).str.strip().str.lower().eq("walk")] if "GeneralEvent" in frame else frame


def extract_file(path, config):
    header=pd.read_csv(path, nrows=0)
    if not {"Time", "L Foot Contact", "R Foot Contact"}.issubset(header): return None
    use=[c for c in ["Time","GeneralEvent","L Foot Contact","R Foot Contact","L_Wrist_Pitch","R_Wrist_Pitch","Xiphoid_Gyr_Z","LowerBack_Acc_X"] if c in header]
    frame=_walk(pd.read_csv(path,usecols=use,low_memory=False)); time=_seconds(frame.Time)
    left=_rising_edges(frame["L Foot Contact"],time); right=_rising_edges(frame["R Foot Contact"],time)
    item=longbout_variability(left,right,minimum_cycles=config["minimum_cycles"], interval_min=config["quality"]["interval_min_seconds"],interval_max=config["quality"]["interval_max_seconds"])
    item["longbout_status"] = item.pop("status")
    p, session=_participant_session(Path(path)); item.update(participant_id=p,session_id=session,site=derive_site(p),task=canonical_task(infer_task(Path(path)) or "unknown"),source="contact_csv")
    steps=np.diff(np.sort(np.r_[left,right])); item["convergence"] = convergence_errors(steps,config["convergence"]["grid"])
    if {"L_Wrist_Pitch","R_Wrist_Pitch"}.issubset(frame):
        arm=arm_features(frame.L_Wrist_Pitch,frame.R_Wrist_Pitch); item.update({f"arm_{k}":v for k,v in arm.items()})
    if "Xiphoid_Gyr_Z" in frame and len(time)>2:
        hz=1/np.nanmedian(np.diff(time)); item.update({f"axial_{k}":v for k,v in axial_rotation_smoothness(frame.Xiphoid_Gyr_Z,hz).items()})
        turn=turning_features(frame.Xiphoid_Gyr_Z,hz); item.update({f"turn_{k}":v for k,v in turn.items()})
    if "LowerBack_Acc_X" in frame: item["harmonic_ratio_ap_v1"], item["stride_regularity_ap_v1"] = harmonic_ratio(frame.LowerBack_Acc_X), stride_regularity(frame.LowerBack_Acc_X,max(1,len(frame)//10))
    return item


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--source",required=True); ap.add_argument("--config",default="configs/v4_analysis.yaml"); ap.add_argument("--output",default="results/v4/frozen"); args=ap.parse_args()
    config=yaml.safe_load(Path(args.config).read_text()); rows=[]; errors=[]
    for path in sorted(Path(args.source).rglob("*.csv")):
        try:
            item=extract_file(path,config)
            if item: rows.append(item)
        except (OSError, ValueError, KeyError): errors.append(Path(path).name)
    output=Path(args.output); output.mkdir(parents=True,exist_ok=True)
    convergence=[{"n_cycles":e["n_cycles"],"relative_error":e["relative_error"]} for row in rows for e in row.pop("convergence")]
    selected=choose_minimum_cycles(convergence,median_max=config["convergence"]["median_relative_error_max"],p90_max=config["convergence"]["p90_relative_error_max"])
    pd.DataFrame(convergence).to_csv(output/"measurement_validation.csv",index=False)
    pd.DataFrame(rows).drop(columns=[c for c in ["participant_id"] if c in pd.DataFrame(rows)],errors="ignore").to_csv(output/"arm_axial_features.csv",index=False)
    (output/"measurement_qc.json").write_text(json.dumps({"n_recordings":len(rows),"read_errors":len(errors),"selected_minimum_cycles":selected,"outcome_blind":True},indent=2)+"\n")


if __name__ == "__main__": main()
