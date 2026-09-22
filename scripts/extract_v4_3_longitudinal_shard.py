#!/usr/bin/env python3
"""Deterministic reconstruction shard for constrained interactive runners."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

from src.v4_3.walkway_reconstruction import reconstruct_csv


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--longitudinal-root", required=True, type=Path)
    parser.add_argument("--shard", required=True, type=int)
    parser.add_argument("--shards", required=True, type=int)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    files = sorted((args.longitudinal_root / "PD Participants" / "00-CSV files").glob("*s[12]_*.csv"))
    expression = re.compile(r"(?P<participant>.+?)s(?P<session>[12])_(?P<task>SelfPace|HurriedPace)$")
    rows, exclusions = [], []
    for path in files[args.shard::args.shards]:
        match = expression.fullmatch(path.stem)
        if not match:
            continue
        try:
            rows.append({**match.groupdict(), "source_file": str(path), **reconstruct_csv(str(path))})
        except (ValueError, pd.errors.ParserError) as error:
            exclusions.append({**match.groupdict(), "source_file": str(path), "reason": str(error)})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.output, index=False)
    pd.DataFrame(exclusions).to_csv(args.output.with_name(args.output.stem + "_exclusions.csv"), index=False)


if __name__ == "__main__":
    main()

