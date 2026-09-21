"""Agreement summaries with conservative explicit gates."""
from __future__ import annotations
import numpy as np
from scipy.stats import pearsonr,spearmanr
def ccc(x,y):
    x,y=np.asarray(x,float),np.asarray(y,float); return float(2*np.cov(x,y,ddof=1)[0,1]/(np.var(x,ddof=1)+np.var(y,ddof=1)+(x.mean()-y.mean())**2))
def agreement(x,y):
    x,y=np.asarray(x,float),np.asarray(y,float); diff=x-y
    return {"n":len(x),"pearson_r":float(pearsonr(x,y).statistic),"spearman_rho":float(spearmanr(x,y).statistic),"ccc":ccc(x,y),"mean_bias":float(diff.mean()),"mae":float(np.abs(diff).mean()),"rmse":float(np.sqrt(np.mean(diff**2))),"ba_low":float(diff.mean()-1.96*diff.std(ddof=1)),"ba_high":float(diff.mean()+1.96*diff.std(ddof=1))}
