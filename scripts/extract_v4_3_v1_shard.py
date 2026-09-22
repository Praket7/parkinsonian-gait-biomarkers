#!/usr/bin/env python3
"""Write one deterministic shard of the V1 raw-walkway reconstruction."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from run_v4_3_v1_equivalence import raw_files, truth_table
from src.v4_3.walkway_reconstruction import reconstruct_csv


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v1-root", required=True, type=Path)
    parser.add_argument("--shard", required=True, type=int)
    parser.add_argument("--shards", required=True, type=int)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if not 0 <= args.shard < args.shards:
        raise SystemExit("shard must be in [0, shards)")
    truth = truth_table(args.v1_root / "Walkway-derived metrics" / "PKMAS Walkway Gait Metrics - HP+SP.csv")
    truth["task"] = truth.task.astype(str).str.strip()
    truth["participant"] = truth.participant.astype(str).str.strip()
    paths = sorted(raw_files(args.v1_root, set(zip(truth.participant, truth.task))))[args.shard::args.shards]
    rows, exclusions = [], []
    for path in paths:
        participant, task = path.stem.split("_", 1)
        try:
            rows.append({"participant": participant, "task": task, **reconstruct_csv(str(path))})
        except (ValueError, pd.errors.ParserError) as error:
            exclusions.append({"participant": participant, "task": task, "reason": str(error)})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.output, index=False)
    pd.DataFrame(exclusions).to_csv(args.output.with_name(args.output.stem + "_exclusions.csv"), index=False)


if __name__ == "__main__":
    main()

