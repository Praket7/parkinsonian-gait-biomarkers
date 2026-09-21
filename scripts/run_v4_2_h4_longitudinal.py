#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import pandas as pd
from check_v4_2_freeze import check
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',default='results/v4_2/frozen');a=p.parse_args()
 if check():raise SystemExit('\n'.join(check()))
 out=Path(a.output);pd.DataFrame([{'feature':'context_adjusted_gait_deviation_v1','estimability_status':'NOT_ESTIMABLE','long_term_stability':'INCOMPLETE','reason':'V1_ANALYTICAL_EQUIVALENCE_NOT_ESTABLISHED_FOR_ALL_EIGHT_INPUTS','n_participants':0}]).to_csv(out/'normative_longitudinal_stability.csv',index=False)
 pd.DataFrame(columns=['task','n_sessions','n_participants']).to_csv(out/'longitudinal_reconstructed_features_qc.csv',index=False)
if __name__=='__main__':main()
