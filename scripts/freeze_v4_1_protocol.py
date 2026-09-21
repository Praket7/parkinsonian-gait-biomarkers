#!/usr/bin/env python3
"""Freeze the v4.1 source and declared analyses before clinical outputs."""
from __future__ import annotations
import hashlib, json, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    files = [ROOT/"configs/v4_1_analysis.yaml", ROOT/"docs/v4_1_preregistration.md", ROOT/"docs/v4_1_validation_questions.md", *sorted((ROOT/"src/v4_1").glob("*.py")), *sorted((ROOT/"scripts").glob("run_v4_1_*.py"))]
    manifest = {"schema":"v4.1-protocol-freeze-v1", "analysis_freeze_commit_sha":os.environ.get("V4_1_FREEZE_COMMIT", "UNAVAILABLE"), "files":{str(path.relative_to(ROOT)):digest(path) for path in files}}
    output=ROOT/"results/v4_1/frozen/protocol_manifest.json"; output.parent.mkdir(parents=True,exist_ok=True); output.write_text(json.dumps(manifest,indent=2)+"\n")
if __name__ == "__main__": main()
