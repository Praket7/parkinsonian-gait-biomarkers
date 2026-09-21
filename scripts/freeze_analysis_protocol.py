#!/usr/bin/env python3
"""Write a content-addressed v3.2 analysis freeze; no results are read."""
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path

def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("--config",required=True); p.add_argument("--prereg",required=True); p.add_argument("--mapping",required=True); p.add_argument("--output",required=True); a=p.parse_args()
    files={"analysis_config_sha256":Path(a.config),"analysis_protocol_sha256":Path(a.prereg),"feature_mapping_sha256":Path(a.mapping)}
    try: commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    except Exception: commit="UNAVAILABLE"
    manifest={key:sha(path) for key,path in files.items()}|{"analysis_freeze_commit_sha":commit,"schema":"analysis-freeze-v1"}
    Path(a.output).parent.mkdir(parents=True,exist_ok=True); Path(a.output).write_text(json.dumps(manifest,indent=2)+"\n"); print(a.output); return 0
if __name__ == "__main__": raise SystemExit(main())
