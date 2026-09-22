"""Repeated participant-disjoint OLS/Ridge validation for the unchanged H2 predictors."""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.stats import pearsonr,spearmanr
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression,Ridge
from sklearn.metrics import log_loss
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler

BASE=["age","height_m","sex","task","site","gait_speed"]
NUM=["age","height_m","gait_speed","context_adjusted_gait_deviation_v1"]
CAT=["sex","task","site"]
def favorable_fraction(group, metric):
    if metric in ("calibration_intercept", "calibration_slope"):
        target = 0 if metric.endswith("intercept") else 1
        return float(((group[f"extended_{metric}"]-target).abs() < (group[f"baseline_{metric}"]-target).abs()).mean())
    delta = group[f"delta_{metric}"]
    return float((delta < 0).mean()) if metric in ("mae", "rmse") else float((delta > 0).mean())
def metric(y,p):
    slope,intercept=np.polyfit(p,y,1) if np.std(p) else (np.nan,np.nan)
    return {"mae":float(np.abs(y-p).mean()),"rmse":float(np.sqrt(np.mean((y-p)**2))),"spearman_rho":float(spearmanr(y,p).statistic),"pearson_r":float(pearsonr(y,p).statistic),"calibration_slope":float(slope),"calibration_intercept":float(intercept)}
def estimator(extended,ridge_alpha=None):
    cols=BASE+(["context_adjusted_gait_deviation_v1"] if extended else [])
    numeric=[c for c in cols if c in NUM]; categorical=[c for c in cols if c in CAT]
    prep=ColumnTransformer([("n",StandardScaler(),numeric),("c",OneHotEncoder(handle_unknown="ignore"),categorical)])
    return make_pipeline(prep,Ridge(alpha=ridge_alpha) if ridge_alpha is not None else LinearRegression()),cols
def run(frame,repetitions,seeds,ridge_alpha=None):
    all_rows=[]
    for rep,seed in enumerate(seeds[:repetitions],1):
        splitter=GroupKFold(n_splits=5,shuffle=True,random_state=int(seed)); predictions=[]
        for fold,(train,test) in enumerate(splitter.split(frame,groups=frame.participant_id),1):
            for name,extended in (("baseline",False),("extended",True)):
                model,cols=estimator(extended,ridge_alpha); model.fit(frame.iloc[train][cols],frame.iloc[train].severity); p=model.predict(frame.iloc[test][cols])
                predictions.extend({"repetition":rep,"fold":fold,"model":name,"participant_id":frame.iloc[i].participant_id,"severity":frame.iloc[i].severity,"prediction":value} for i,value in zip(test,p))
        pred=pd.DataFrame(predictions)
        for level,table in (("row",pred),("participant",pred.groupby(["model","participant_id"],as_index=False).agg(severity=("severity","mean"),prediction=("prediction","mean")).assign(repetition=rep))):
            values={name:metric(group.severity.to_numpy(),group.prediction.to_numpy()) for name,group in table.groupby("model")}
            all_rows.append({"repetition":rep,"level":level,**{f"baseline_{k}":v for k,v in values["baseline"].items()},**{f"extended_{k}":v for k,v in values["extended"].items()},**{f"delta_{k}":values["extended"][k]-values["baseline"][k] for k in values["baseline"]}})
    return pd.DataFrame(all_rows)
