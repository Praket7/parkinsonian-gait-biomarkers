#!/usr/bin/env python3
"""Execute the frozen v4.6 analyses in their prespecified order."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(*args: str) -> None:
    subprocess.run([sys.executable, *args], check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v1-root", required=True, type=Path)
    parser.add_argument("--matched", type=Path, default=Path("results/v4_3/v1_reconstructed_features.csv"))
    parser.add_argument("--endpoints", type=Path, default=Path("results/v4_4/h4b_session_endpoints_local.csv"))
    parser.add_argument("--output", type=Path, default=Path("results/v4_6"))
    args = parser.parse_args()
    run("scripts/check_v4_6_freeze.py")
    run("scripts/run_v4_6_score_agreement.py", "--v1-root", str(args.v1_root), "--input", str(args.matched), "--output", str(args.output))
    run("scripts/run_v4_6_deviation_geometry.py", "--input", str(args.endpoints), "--output", str(args.output))
    run("scripts/run_v4_6_reference_uncertainty.py", "--v1-root", str(args.v1_root), "--endpoints", str(args.endpoints), "--output", str(args.output))
    run("scripts/build_v4_6_report.py", "--output", str(args.output))
    run("scripts/check_v4_6_claims.py", str(args.output / "v4_6_failure_mode_report.md"))


if __name__ == "__main__":
    main()
