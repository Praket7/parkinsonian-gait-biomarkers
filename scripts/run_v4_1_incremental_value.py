#!/usr/bin/env python3
"""Frozen grouped held-out OLS comparison for v4.1 H2."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import yaml
from check_v4_1_freeze import check
from run_v4_1_normative_validation import load
from src.v4_1.normative import fit_reference, score
from src.v4_1.validation import bootstrap_group_deltas, grouped_folds, metrics

BASE=("age","height_m","sex","task","site")
MODELS={"model_0":BASE,"model_1":BASE+("gait_speed",),"model_2":BASE+("gait_speed","context_adjusted_gait_deviation_v1"),"model_3_descriptive":BASE+("context_adjusted_gait_deviation_v1",)}
def design(frame, columns, categories):
    numeric=[column for column in columns if column in {"age","height_m","gait_speed","context_adjusted_gait_deviation_v1"}]
    output=[np.ones(len(frame)), *[pd.to_numeric(frame[column],errors="coerce").to_numpy(float) for column in numeric]]
    for column in (item for item in columns if item not in numeric):
        output.extend((frame[column].astype(str).to_numpy()==level).astype(float) for level in categories[column][1:])
    return np.column_stack(output)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--source",required=True); ap.add_argument("--config",default="configs/v4_1_analysis.yaml"); ap.add_argument("--output",default="results/v4_1/frozen"); args=ap.parse_args()
    failures=check()
    if failures: raise SystemExit("\n".join(failures))
    config=yaml.safe_load(Path(args.config).read_text()); output=Path(args.output); full=load(args.source); controls=full[full.clinical_cohort.eq("control")]; pd_rows=full[full.clinical_cohort.eq("pd")].copy()
    pd_rows["context_adjusted_gait_deviation_v1"]=score(pd_rows,fit_reference(controls)); pd_rows["severity"]=pd.to_numeric(pd_rows.mds_updrs_gait_item,errors="coerce")
    pd_rows=pd_rows.dropna(subset=["severity",*BASE,"gait_speed","context_adjusted_gait_deviation_v1"]).copy(); categories={column:sorted(pd_rows[column].astype(str).unique()) for column in ("sex","task","site")}
    predicted={name:np.full(len(pd_rows),np.nan) for name in MODELS}
    for train,test in grouped_folds(pd_rows,"participant_id",5):
        for name,columns in MODELS.items():
            x_train,x_test=design(pd_rows.iloc[train],columns,categories),design(pd_rows.iloc[test],columns,categories)
            beta=np.linalg.lstsq(x_train,pd_rows.iloc[train].severity.to_numpy(float),rcond=None)[0]; predicted[name][test]=x_test@beta
    pool=pd.DataFrame({"participant_id":pd_rows.participant_id,"severity":pd_rows.severity,**predicted})
    report=[]
    for name in MODELS: report.append({"model":name,"n_participants":int(pool.participant_id.nunique()),"n_heldout_rows":len(pool),**metrics(pool.severity,pool[name])})
    pd.DataFrame(report).to_csv(output/"incremental_prediction.csv",index=False)
    bootstrap_group_deltas(pool,"model_1","model_2",config["prediction_bootstrap_iterations"],config["seed"]+1).to_csv(output/"incremental_bootstrap.csv",index=False)
if __name__=="__main__": main()
