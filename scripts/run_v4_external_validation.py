#!/usr/bin/env python3
"""Frozen aggregate-only v4 external routes: Mobilise-D and official CARE-PD."""
from __future__ import annotations
import argparse
from pathlib import Path
import yaml
from check_v4_freeze import check
from src.mobilised_cvs import load_pd_dataset, build_mobilised_canonical
from src.v4.mobilised_stability import stability_selection
from src.v4.carepd_matched import run as carepd_run


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--mobilised",required=True); ap.add_argument("--carepd",required=True); ap.add_argument("--output",default="results/v4/frozen"); args=ap.parse_args()
    if failures:=check(): raise SystemExit("\n".join(failures))
    output=Path(args.output); output.mkdir(parents=True,exist_ok=True)
    canonical=build_mobilised_canonical(load_pd_dataset(Path(args.mobilised)))
    stability_selection(canonical,["gait_speed","stride_length_mean","cadence","stride_time_mean"],seed=20260921).to_csv(output/"mobilised_stability.csv",index=False)
    carepd_run(Path(args.carepd),min_participants=8).to_csv(output/"carepd_replication.csv",index=False)


if __name__ == "__main__": main()
