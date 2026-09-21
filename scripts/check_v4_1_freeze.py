#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def check():
    path=ROOT/"results/v4_1/frozen/protocol_manifest.json"
    if not path.exists(): return ["missing v4.1 protocol manifest"]
    try: manifest=json.loads(path.read_text())
    except json.JSONDecodeError: return ["invalid v4.1 protocol manifest"]
    if manifest.get("schema")!="v4.1-protocol-freeze-v1": return ["invalid v4.1 freeze schema"]
    return [f"v4.1 freeze mismatch: {name}" for name, expected in manifest.get("files",{}).items() if not (ROOT/name).exists() or hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=expected]
if __name__=="__main__":
    failures=check(); print("v4.1 freeze check passed" if not failures else "\n".join(failures)); raise SystemExit(bool(failures))
