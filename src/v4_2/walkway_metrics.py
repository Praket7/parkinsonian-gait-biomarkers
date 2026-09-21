"""PKMAS-conceptual time summaries from validated footfall events."""
from __future__ import annotations
import numpy as np
import pandas as pd

def summarize_contacts(events: pd.DataFrame) -> dict:
    values=events.sort_values("time").reset_index(drop=True); step=values.time.diff().iloc[1:].to_numpy(float)
    stride=[]
    for foot in ("L","R"):
        stride.extend(values.loc[values.foot.eq(foot),"time"].diff().dropna().to_numpy(float))
    if len(step)<3 or len(stride)<3: raise ValueError("insufficient valid contacts")
    return {"step_time_mean":float(np.mean(step)),"stride_time_mean":float(np.mean(stride)),"step_time_cv":float(100*np.std(step,ddof=1)/np.mean(step)),"stride_time_cv":float(100*np.std(stride,ddof=1)/np.mean(stride)),"cadence":float(60*len(step)/(values.time.iloc[-1]-values.time.iloc[0]))}
