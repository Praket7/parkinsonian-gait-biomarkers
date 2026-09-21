#!/usr/bin/env python3
import argparse
from pathlib import Path
import pandas as pd
from check_v4_2_freeze import check
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',default='results/v4_2/frozen');a=p.parse_args()
 if check():raise SystemExit('\n'.join(check()))
 pd.DataFrame([{'analysis':'within_session_technical_precision','estimability_status':'NOT_ESTIMABLE','reason':'H4_ANALYTICAL_EQUIVALENCE_GATE_NOT_MET'}]).to_csv(Path(a.output)/'normative_within_session_precision.csv',index=False)
if __name__=='__main__':main()
