#!/usr/bin/env python3
"""Nested participant-grouped ridge sensitivity with frozen alpha grid."""
import argparse
from pathlib import Path
import numpy as np,pandas as pd,yaml
from sklearn.model_selection import GroupKFold
from check_v4_2_freeze import check
from run_v4_2_h2_repeated_cv import data
from src.v4_2.repeated_group_cv import estimator,metric
def choose(frame,extended,grid):
 scores=[]
 for alpha in grid:
  vals=[]
  for train,test in GroupKFold(n_splits=4).split(frame,groups=frame.participant_id):
   model,cols=estimator(extended,alpha);model.fit(frame.iloc[train][cols],frame.iloc[train].severity);vals.append(metric(frame.iloc[test].severity,model.predict(frame.iloc[test][cols]))['rmse'])
  scores.append(np.mean(vals))
 return grid[int(np.argmin(scores))]
def main():
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--config',default='configs/v4_2_analysis.yaml');p.add_argument('--output',default='results/v4_2/frozen');a=p.parse_args()
 if check():raise SystemExit('\n'.join(check()))
 c=yaml.safe_load(Path(a.config).read_text());frame=data(a.source);out=[]
 for rep,seed in enumerate(range(c['seed'],c['seed']+c['h2_repetitions']),1):
  predictions=[]
  for train,test in GroupKFold(n_splits=5,shuffle=True,random_state=seed).split(frame,groups=frame.participant_id):
   for name,extended in [('baseline',False),('extended',True)]:
    alpha=choose(frame.iloc[train],extended,c['ridge_alpha_grid']);model,cols=estimator(extended,alpha);model.fit(frame.iloc[train][cols],frame.iloc[train].severity)
    predictions.extend((name,frame.iloc[i].severity,value) for i,value in zip(test,model.predict(frame.iloc[test][cols])))
  pred=pd.DataFrame(predictions,columns=['model','severity','prediction']);m={n:metric(g.severity,g.prediction) for n,g in pred.groupby('model')};out.append({'repetition':rep,**{f'delta_{k}':m['extended'][k]-m['baseline'][k] for k in m['baseline']}})
 rows=pd.DataFrame(out);rows.to_csv(Path(a.output)/'h2_ridge_runs.csv',index=False);rows.median(numeric_only=True).to_frame().T.to_csv(Path(a.output)/'h2_ridge_summary.csv',index=False)
if __name__=='__main__':main()
