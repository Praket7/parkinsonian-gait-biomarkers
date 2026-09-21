#!/usr/bin/env python3
"""Run frozen v4 clinical inference only after the outcome-blind measurement freeze."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
import yaml
from check_v4_freeze import check
from run_v4_measurement_validation import extract_file
from src.walkway import load_walkway_metrics
from src.weargait_clinical import load_v1_clinical, join_clinical_features
from src.stats_v3 import association_table, gee_bootstrap, participant_permutations
from src.v4.normative_deviation import fit_controls, score
from src.v4.speed_response import response_indices
from src.v4.evidence_synthesis import build_evidence
from src.stats import bh_fdr


def _paths(root):
    return (root / "Walkway-derived metrics/PKMAS Walkway Gait Metrics - HP+SP.csv",
            root / "PD - Demographic+Clinical - datasetV1.csv", root / "CONTROLS - Demographic+Clinical - datasetV1.csv")


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--source",required=True); ap.add_argument("--config",default="configs/v4_analysis.yaml"); ap.add_argument("--output",default="results/v4/frozen"); args=ap.parse_args()
    failures=check()
    if failures: raise SystemExit("\n".join(failures))
    config=yaml.safe_load(Path(args.config).read_text()); root=Path(args.source); walkway_path,pd_path,control_path=_paths(root)
    walkway=load_walkway_metrics(walkway_path); clinical=load_v1_clinical(pd_path,control_path); full=join_clinical_features(walkway,clinical)
    features=["gait_speed","cadence","step_length_mean","stride_length_mean","step_time_mean","stride_time_mean","step_time_cv","stride_time_cv"]
    controls=full[full.clinical_cohort.eq("control")].copy()
    model=fit_controls(controls,features); full["context_adjusted_gait_deviation_v1"]=score(full,model)
    scaling=response_indices(full).merge(clinical,on="participant_id",how="left")
    # Outcome-blind measurement data are recomputed from the frozen extractor;
    # clinical fields are joined only here, after freeze validation.
    contacts=[]
    for path in sorted(root.rglob("*.csv")):
        if "FW" not in set(config["contact_association_tasks"]) or "FreeWalk" not in path.stem:
            continue
        try:
            item=extract_file(path,config)
            if item and item.get("longbout_status")=="OK": contacts.append(item)
        except (OSError,ValueError,KeyError): pass
    contact=pd.DataFrame(contacts)
    if not contact.empty:
        contact=contact.drop(columns="convergence",errors="ignore").merge(clinical,on="participant_id",how="left")
    candidate="step_time_cv_longbout_v1"
    primary=pd.concat([full[full.clinical_cohort.eq("pd")], scaling.assign(task="SP",site=scaling.participant_id.str.extract(r"([A-Za-z]+)")[0],session_id="v1",clinical_cohort="pd")],ignore_index=True,sort=False)
    associations=association_table(primary,["context_adjusted_gait_deviation_v1",*list(scaling.filter(regex="_v1$").columns)],config) if not scaling.empty else association_table(primary,["context_adjusted_gait_deviation_v1"],config)
    if not contact.empty:
        contact_pd=contact[contact.clinical_cohort.eq("pd")]
        # Free-walking contact exports have no validated spatial speed route.
        # Keep the prespecified speed-adjustment gate visible as NOT_ESTIMABLE.
        contact_pd["gait_speed"] = np.nan
        contact_features=[c for c in config["families"]["variability_rescue"] + config["families"]["arm_axial"] + config["families"]["turning"] + config["families"]["harmonicity"] if c in contact_pd and contact_pd[c].notna().sum()]
        contact_assoc=association_table(contact_pd,contact_features,config)
        associations=pd.concat([associations,contact_assoc],ignore_index=True)
        boot=gee_bootstrap(contact_pd,contact_assoc,config); perm=participant_permutations(contact_pd,contact_features,config)
        associations=associations.merge(boot,on="feature",how="left").merge(perm,on="feature",how="left")
    definitions=yaml.safe_load(Path("configs/v4_feature_definitions.yaml").read_text())
    for feature, meta in definitions.items():
        meta["speed_construct"] = config["speed_construct"].get(feature, "not_applicable")
    for _, indexes in associations.groupby(associations.feature.map(lambda x: definitions.get(x,{}).get("construct","unknown"))).groups.items():
        associations.loc[indexes,"q_value"] = bh_fdr(associations.loc[indexes,"p_value"])
    output=Path(args.output); output.mkdir(parents=True,exist_ok=True)
    associations.to_csv(output/"primary_associations.csv",index=False)
    full.groupby("clinical_cohort")["context_adjusted_gait_deviation_v1"].agg(["count","mean","std"]).reset_index().to_csv(output/"normative_deviation.csv",index=False)
    scaling.groupby("clinical_cohort",dropna=False)[["delta_speed","stride_scaling_response_v1","cadence_scaling_response_v1"]].agg(["count","mean","std","median"]).to_csv(output/"speed_response.csv")
    build_evidence(associations,definitions).to_csv(output/"evidence_matrix.csv",index=False)
    (output/"primary_qc.json").write_text(json.dumps({"freeze_checked":True,"n_pd":int(full.clinical_cohort.eq("pd").sum()),"n_contact_recordings":len(contact),"clinical_outcomes_accessed_after_freeze":True},indent=2)+"\n")


if __name__ == "__main__": main()
