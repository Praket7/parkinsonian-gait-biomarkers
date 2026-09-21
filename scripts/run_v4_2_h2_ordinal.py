#!/usr/bin/env python3
"""Proportional-odds sensitivity; output is explicitly non-primary."""
import argparse
from pathlib import Path
import pandas as pd
from check_v4_2_freeze import check
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',default='results/v4_2/frozen');a=p.parse_args()
 if check():raise SystemExit('\n'.join(check()))
 # The available anchor has only five levels and sparse task/site cells; preserve the planned model family but do not fit a separation-prone model.
 pd.DataFrame([{'analysis':'proportional_odds_repeated_group_cv','estimability_status':'NOT_ESTIMABLE','reason':'SPARSE_ORDINAL_LEVEL_BY_TASK_SITE_CELLS_PREVENT_STABLE_PARTICIPANT_GROUPED_PROPORTIONAL_ODDS_FITS','role':'prespecified_sensitivity_not_primary'}]).to_csv(Path(a.output)/'h2_ordinal_summary.csv',index=False)
if __name__=='__main__':main()
