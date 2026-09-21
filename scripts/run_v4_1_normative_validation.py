#!/usr/bin/env python3
"""Run the frozen v4.1 H1/H3 control-reference validation on authorized V1 data."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
import yaml
from check_v4_1_freeze import check
from src.walkway import load_walkway_metrics
from src.weargait_clinical import load_v1_clinical, join_clinical_features
from src.stats_v3 import gee_association
from src.v4_1.normative import FEATURES, fit_reference, score, serialize
from src.v4_1.validation import grouped_folds

def load(source):
    root=Path(source); walkway=load_walkway_metrics(root/"Walkway-derived metrics/PKMAS Walkway Gait Metrics - HP+SP.csv")
    clinical=load_v1_clinical(root/"PD - Demographic+Clinical - datasetV1.csv",root/"CONTROLS - Demographic+Clinical - datasetV1.csv")
    return join_clinical_features(walkway,clinical)

def association(pd_rows):
    full=gee_association(pd_rows,"context_adjusted_gait_deviation_v1",minimum_participants=20)
    speed=gee_association(pd_rows,"context_adjusted_gait_deviation_v1",speed_adjusted=True,minimum_participants=20)
    return full, speed

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--source",required=True); ap.add_argument("--config",default="configs/v4_1_analysis.yaml"); ap.add_argument("--output",default="results/v4_1/frozen"); args=ap.parse_args()
    failures=check()
    if failures: raise SystemExit("\n".join(failures))
    config=yaml.safe_load(Path(args.config).read_text()); output=Path(args.output); output.mkdir(parents=True,exist_ok=True)
    full=load(args.source); controls=full[full.clinical_cohort.eq("control")].copy(); pd_rows=full[full.clinical_cohort.eq("pd")].copy()
    model=fit_reference(controls); pd_rows["context_adjusted_gait_deviation_v1"]=score(pd_rows,model)
    baseline, baseline_speed=association(pd_rows)
    cross=[]
    for fold,(train,test) in enumerate(grouped_folds(controls,"participant_id",config["control_crossfit_folds"]),1):
        held=controls.iloc[test].copy(); held["context_adjusted_gait_deviation_v1"]=score(held,fit_reference(controls.iloc[train]))
        cross.append({"fold":fold,"n_train_control_participants":int(controls.iloc[train].participant_id.nunique()),"n_heldout_control_participants":int(held.participant_id.nunique()),"n_heldout_rows":len(held),"score_mean":float(held.context_adjusted_gait_deviation_v1.mean()),"score_sd":float(held.context_adjusted_gait_deviation_v1.std(ddof=1))})
    pd.DataFrame(cross).to_csv(output/"normative_crossfit_controls.csv",index=False)
    cov=[]
    for method in config["frozen_covariance_methods"]:
        candidate=pd_rows.copy(); candidate["context_adjusted_gait_deviation_v1"]=score(candidate,fit_reference(controls,covariance_method=method)); a,b=association(candidate)
        cov.append({"covariance_method":method,"effect":a["effect"],"ci_low":a["ci_low"],"ci_high":a["ci_high"],"speed_adjusted_effect":b["effect"],"speed_adjusted_ci_low":b["ci_low"],"speed_adjusted_ci_high":b["ci_high"],"association_status":a["status"],"speed_adjusted_status":b["status"]})
    pd.DataFrame(cov).to_csv(output/"normative_covariance_sensitivity.csv",index=False)
    rng, people=np.random.default_rng(config["seed"]),controls.participant_id.unique(); boot=[]
    for index in range(config["control_bootstrap_iterations"]):
        chosen=rng.choice(people,len(people),replace=True)
        sampled=pd.concat([controls[controls.participant_id.eq(person)].assign(participant_id=f"control_boot_{j}") for j,person in enumerate(chosen)],ignore_index=True)
        candidate=pd_rows.copy(); candidate["context_adjusted_gait_deviation_v1"]=score(candidate,fit_reference(sampled)); a,b=association(candidate)
        boot.append({"resample":index+1,"effect":a["effect"],"ci_low":a["ci_low"],"ci_high":a["ci_high"],"direction":float(np.sign(a["effect"])),"speed_adjusted_effect":b["effect"],"speed_adjusted_ci_low":b["ci_low"],"speed_adjusted_ci_high":b["ci_high"],"speed_adjusted_direction":float(np.sign(b["effect"]))})
    bootstrap=pd.DataFrame(boot); bootstrap.to_csv(output/"normative_reference_bootstrap.csv",index=False)
    ablation=[]
    for removed in FEATURES:
        features=[item for item in FEATURES if item!=removed]; candidate=pd_rows.copy(); candidate["context_adjusted_gait_deviation_v1"]=score(candidate,fit_reference(controls,features)); a,b=association(candidate)
        ablation.append({"removed_feature":removed,"effect":a["effect"],"ci_low":a["ci_low"],"ci_high":a["ci_high"],"speed_adjusted_effect":b["effect"],"speed_adjusted_ci_low":b["ci_low"],"speed_adjusted_ci_high":b["ci_high"],"same_direction_as_full_score":bool(np.sign(a["effect"])==np.sign(baseline["effect"])),"relative_effect_change":float((a["effect"]-baseline["effect"])/abs(baseline["effect"]))})
    pd.DataFrame(ablation).to_csv(output/"normative_leave_one_feature_out.csv",index=False)
    domains={"pace":["gait_speed","step_length_mean","stride_length_mean"],"rhythm":["cadence","step_time_mean","stride_time_mean"],"variability":["step_time_cv","stride_time_cv"]}; domain=[]
    for name,features in domains.items():
        held=controls.copy(); held["score"]=score(held,fit_reference(controls,features)); domain.append({"domain":name,"n_inputs":len(features),"control_score_mean":float(held.score.mean()),"control_score_sd":float(held.score.std(ddof=1))})
    pd.DataFrame(domain).to_csv(output/"normative_domain_contributions.csv",index=False)
    (output/"v4_1_control_model.json").write_text(json.dumps({**serialize(model),"provenance":"v4.0.6-compatible V1 control reference; no clinical outcomes used in fitting"},indent=2)+"\n")
    summary={"association_effect":baseline["effect"],"speed_adjusted_effect":baseline_speed["effect"],"bootstrap_same_direction_fraction":float((bootstrap.direction==np.sign(baseline["effect"])).mean()),"bootstrap_median_effect":float(bootstrap.effect.median()),"h1_status":"PASS" if (bootstrap.direction==np.sign(baseline["effect"])).mean()>=.8 and bootstrap.effect.median()>0 else "FAIL"}
    (output/"normative_validation_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
if __name__=="__main__": main()
