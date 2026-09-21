#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def check():
    path = ROOT / "results/v4/frozen/protocol_manifest.json"
    if not path.exists(): return ["missing v4 protocol manifest"]
    try: manifest = json.loads(path.read_text())
    except json.JSONDecodeError: return ["invalid v4 protocol manifest"]
    if manifest.get("schema") != "v4-protocol-freeze-v1": return ["invalid v4 freeze schema"]
    failures=[]
    for relative, expected in manifest.get("files", {}).items():
        source=ROOT/relative
        actual=hashlib.sha256(source.read_bytes()).hexdigest() if source.exists() else None
        if actual != expected: failures.append(f"POST_FREEZE_DEVIATION: {relative}")
    return failures


if __name__ == "__main__":
    failures=check(); print("v4 freeze check passed" if not failures else "\n".join(failures)); raise SystemExit(bool(failures))
