#!/usr/bin/env python3
"""Export the already prespecified participant-level repeated-CV sensitivity."""
import argparse
from pathlib import Path
import pandas as pd
from check_v4_2_freeze import check
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',default='results/v4_2/frozen');a=p.parse_args()
 if check():raise SystemExit('\n'.join(check()))
 runs=pd.read_csv(Path(a.output)/'h2_repeated_cv_runs.csv');runs[runs.level.eq('participant')].to_csv(Path(a.output)/'h2_participant_level_runs.csv',index=False)
if __name__=='__main__':main()
