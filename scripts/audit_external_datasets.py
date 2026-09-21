#!/usr/bin/env python3
"""Metadata/schema audit only; this script never opens participant-level tables."""
from __future__ import annotations
import argparse, json
from pathlib import Path

from src import mendeley_gait, mobilised_cvs, adaptive_dbs

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--data-root"); parser.add_argument("--metadata-only", action="store_true")
    args = parser.parse_args(); root = Path(args.data_root) if args.data_root else None
    if root is None:
        print(json.dumps({"status":"NO_AUTHORIZED_DATA_ROOT","metadata_only":args.metadata_only}, indent=2)); return 0
    result = {"mendeley_gait":mendeley_gait.audit(root / "Mendeley_Gait_PD_v2"), "mobilised_cvs":mobilised_cvs.audit(root / "MobiliseD_CVS_v1_0_0"), "adaptive_dbs":adaptive_dbs.audit(root / "AdaptiveDBS_Gait_2026")}
    print(json.dumps(result, indent=2)); return 0
if __name__ == "__main__": raise SystemExit(main())
