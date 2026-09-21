#!/usr/bin/env python3
"""Explicitly close unvalidated eight-input external transport without a crosswalk."""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from check_v4_1_freeze import check
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",default="results/v4_1/frozen"); args=ap.parse_args()
    failures=check()
    if failures: raise SystemExit("\n".join(failures))
    output=Path(args.output); output.mkdir(parents=True,exist_ok=True)
    pd.DataFrame([{ "analysis":"eight_input_normative_external_transport","estimability_status":"NOT_ESTIMABLE","transport_status":"INCOMPLETE","reason":"NO_EXTERNAL_RELEASE_WITH_DEFENSIBLE_ALL_EIGHT_INPUT_CROSSWALK_AND_HEALTHY_REFERENCE; NO_POST_HOC_CROSSWALK_CREATED"}]).to_csv(output/"normative_external_transport.csv",index=False)
if __name__=="__main__": main()
