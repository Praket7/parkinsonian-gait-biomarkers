#!/usr/bin/env python3
"""Close H4 conservatively when calibrated raw spatial coordinates are absent."""
import argparse,json
from pathlib import Path
import pandas as pd
from check_v4_2_freeze import check
from src.v4_1.normative import FEATURES
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',default='results/v4_2/frozen');a=p.parse_args()
 if check(): raise SystemExit('\n'.join(check()))
 out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
 rows=[]
 for feature in FEATURES: rows.append({'feature':feature,'estimability_status':'NOT_ESTIMABLE','analytic_equivalence_status':'NOT_ESTIMABLE','reason':'RAW_RELEASE_HAS_NO_DOCUMENTED_CALIBRATED_REAR_FOOT_COORDINATE_FOR_PKMAS_SPATIAL_EQUIVALENCE'})
 pd.DataFrame(rows).to_csv(out/'v1_reconstruction_agreement.csv',index=False);pd.DataFrame(columns=['feature','mean_bias','ba_low','ba_high']).to_csv(out/'v1_reconstruction_bland_altman.csv',index=False)
 (out/'v1_reconstruction_qc.json').write_text(json.dumps({'all_eight_equivalent':False,'h4_status':'NOT_ESTIMABLE','stop_reason':'V1 spatial analytic-equivalence bridge cannot be validated without documented metric coordinate calibration; no longitudinal score generated.'},indent=2)+'\n')
if __name__=='__main__':main()
