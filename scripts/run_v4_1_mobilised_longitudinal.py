#!/usr/bin/env python3
"""Frozen v4.1 within/between Mobilise-D validation (aggregate outputs only)."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
import yaml
from check_v4_1_freeze import check
from src.mobilised_cvs import build_mobilised_canonical, load_pd_dataset, RELEASE_MAPPING

def z(value):
    value=pd.to_numeric(value,errors="coerce"); sd=value.std(ddof=0); return (value-value.mean())/sd if sd else value*np.nan
def fit(table, feature):
    frame=table[["participant_key",feature,"mdsscore3","months_from_baseline","age","height","sex","site"]].dropna().copy()
    frame["anchor_between"]=frame.mdsscore3.groupby(frame.participant_key).transform("mean"); frame["anchor_within"]=frame.mdsscore3-frame.anchor_between
    for column in (feature,"anchor_between","anchor_within","months_from_baseline","age","height"): frame[f"{column}_z"]=z(frame[column])
    if frame.participant_key.nunique()<20 or frame.anchor_within_z.nunique()<2: return {"feature":feature,"estimability_status":"NOT_ESTIMABLE","n_participants":int(frame.participant_key.nunique()),"n_rows":len(frame)}
    try:
        result=sm.GEE.from_formula(f"{feature}_z ~ anchor_within_z + anchor_between_z + months_from_baseline_z + age_z + height_z + C(sex) + C(site)",groups="participant_key",data=frame,family=sm.families.Gaussian(),cov_struct=sm.cov_struct.Exchangeable()).fit()
        ci=result.conf_int().loc["anchor_within_z"]
        return {"feature":feature,"estimability_status":"OK","n_participants":int(frame.participant_key.nunique()),"n_rows":len(frame),"within_effect":float(result.params.anchor_within_z),"within_ci_low":float(ci.iloc[0]),"within_ci_high":float(ci.iloc[1]),"within_p_value":float(result.pvalues.anchor_within_z),"between_effect":float(result.params.anchor_between_z)}
    except Exception: return {"feature":feature,"estimability_status":"FIT_FAILED","n_participants":int(frame.participant_key.nunique()),"n_rows":len(frame)}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--source",required=True); ap.add_argument("--config",default="configs/v4_1_analysis.yaml"); ap.add_argument("--output",default="results/v4_1/frozen"); args=ap.parse_args()
    failures=check()
    if failures: raise SystemExit("\n".join(failures))
    config=yaml.safe_load(Path(args.config).read_text()); output=Path(args.output); output.mkdir(parents=True,exist_ok=True)
    mapping={**RELEASE_MAPPING,"features":{**RELEASE_MAPPING["features"],"strlen_30_avg_w":{"canonical":"stride_length_mean","source_unit":"cm","canonical_unit":"m"}}}
    table=build_mobilised_canonical(load_pd_dataset(Path(args.source),mapping),mapping); features=config["mobilised_features"]
    original=[fit(table,feature) for feature in features]; pd.DataFrame(original).to_csv(output/"mobilised_within_between.csv",index=False)
    rng,people=np.random.default_rng(config["seed"]+2),table.participant_key.unique(); rows=[]
    for number in range(config["mobilised_half_resamples"]):
        chosen=rng.choice(people,max(1,len(people)//2),replace=False); sample=table[table.participant_key.isin(chosen)]
        for feature in features:
            result=fit(sample,feature); rows.append({"resample":number+1,"feature":feature,"within_effect":result.get("within_effect",np.nan),"estimability_status":result["estimability_status"]})
    draws=pd.DataFrame(rows); summaries=[]
    for item in original:
        values=draws.loc[draws.feature.eq(item["feature"]),"within_effect"].dropna(); observed=item.get("within_effect",np.nan)
        summaries.append({**item,"resamples_completed":int(len(values)),"half_sample_median_within_effect":float(values.median()) if len(values) else np.nan,"half_sample_ci_low":float(values.quantile(.025)) if len(values) else np.nan,"half_sample_ci_high":float(values.quantile(.975)) if len(values) else np.nan,"same_direction_fraction":float((np.sign(values)==np.sign(observed)).mean()) if len(values) and np.isfinite(observed) else np.nan,"stability_status":"PASS" if len(values)>=180 and (np.sign(values)==np.sign(observed)).mean()>=.8 else "INCOMPLETE"})
    pd.DataFrame(summaries).to_csv(output/"mobilised_within_between_stability.csv",index=False)
    draws.to_csv(output/"mobilised_within_between_resamples.csv",index=False)
if __name__=="__main__": main()
