#!/usr/bin/env python3
import argparse
from pathlib import Path
import numpy as np,pandas as pd,yaml
from check_v4_2_freeze import check
from run_v4_1_normative_validation import load
from src.v4_1.normative import fit_reference,score
from src.v4_2.repeated_group_cv import run
def data(source):
 x=load(source);x['context_adjusted_gait_deviation_v1']=score(x,fit_reference(x[x.clinical_cohort.eq('control')]));x['severity']=pd.to_numeric(x.mds_updrs_gait_item,errors='coerce');return x[x.clinical_cohort.eq('pd')].dropna(subset=['severity','age','height_m','sex','task','site','gait_speed','context_adjusted_gait_deviation_v1']).copy()
def main():
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--config',default='configs/v4_2_analysis.yaml');p.add_argument('--output',default='results/v4_2/frozen');a=p.parse_args()
 if check():raise SystemExit('\n'.join(check()))
 c=yaml.safe_load(Path(a.config).read_text());result=run(data(a.source),c['h2_repetitions'],np.arange(c['seed'],c['seed']+c['h2_repetitions']));out=Path(a.output);result.to_csv(out/'h2_repeated_cv_runs.csv',index=False)
 summary=[]
 for level,g in result.groupby('level'):
  summary.append({'level':level,**{f'{col}_median':g[col].median() for col in g if col.startswith('delta_')},**{f'{col}_favorable_fraction':float((g[col]<0).mean()) if col in ('delta_mae','delta_rmse') else float((g[col]>0).mean()) for col in g if col.startswith('delta_')}})
 pd.DataFrame(summary).to_csv(out/'h2_repeated_cv_summary.csv',index=False)
if __name__=='__main__':main()
