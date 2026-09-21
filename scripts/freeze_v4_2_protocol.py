#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    files=[ROOT/'configs/v4_2_analysis.yaml',ROOT/'configs/v4_2_walkway_qc.yaml',*sorted((ROOT/'docs').glob('v4_2_*.md')),*sorted((ROOT/'src/v4_2').glob('*.py')),*sorted(ROOT.glob('scripts/*v4_2*.py'))]
    out=ROOT/'results/v4_2/frozen/protocol_manifest.json'; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps({'schema':'v4.2-freeze-v1','commit':os.getenv('V4_2_FREEZE_COMMIT','UNAVAILABLE'),'files':{str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in files}},indent=2)+'\n')
if __name__=='__main__': main()
