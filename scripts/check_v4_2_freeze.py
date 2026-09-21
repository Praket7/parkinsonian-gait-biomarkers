#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def check():
    p=ROOT/'results/v4_2/frozen/protocol_manifest.json'
    if not p.exists(): return ['missing v4.2 freeze']
    m=json.loads(p.read_text()); return [f'v4.2 freeze mismatch: {x}' for x,h in m.get('files',{}).items() if not (ROOT/x).exists() or hashlib.sha256((ROOT/x).read_bytes()).hexdigest()!=h]
if __name__=='__main__':
    f=check(); print('v4.2 freeze check passed' if not f else '\n'.join(f)); raise SystemExit(bool(f))
