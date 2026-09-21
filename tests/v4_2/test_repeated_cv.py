import numpy as np,pandas as pd
from src.v4_2.repeated_group_cv import run
def test_grouped_cv_runs_without_overlap():
    rows=[]
    for p in range(10):
      for task in ['SP','HP']: rows.append({'participant_id':p,'severity':p%5,'age':60+p,'height_m':1.7,'sex':'F','task':task,'site':'x','gait_speed':1+p*.01,'context_adjusted_gait_deviation_v1':p*.1})
    result=run(pd.DataFrame(rows),2,[1,2]);assert len(result)==4 and result.delta_rmse.notna().all()
