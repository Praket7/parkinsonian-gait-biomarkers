#!/usr/bin/env python3
"""Fetch public dataset metadata only; never accepts terms or downloads human data."""
from __future__ import annotations

import hashlib
import json
import pathlib
import urllib.request
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "metadata"
SOURCES = {
    "weargait-synapse-entity.json": "https://repo-prod.prod.sagebase.org/repo/v1/entity/syn52540892",
    "weargait-synapse-wiki.json": "https://repo-prod.prod.sagebase.org/repo/v1/entity/syn52540892/wiki/623751",
    "weargait-access-wiki.json": "https://repo-prod.prod.sagebase.org/repo/v1/entity/syn52540892/wiki/623752",
    "carepd-dataverse-api.json": "https://borealisdata.ca/api/datasets/:persistentId/?persistentId=doi:10.5683/SP3/TWIKMK",
    "carepd-hf-api.json": "https://huggingface.co/api/datasets/vida-adl/CARE-PD",
    "CARE-PD-README.md": "https://raw.githubusercontent.com/TaatiTeam/CARE-PD/master/README.md",
}


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "dataset-metadata-audit/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {"retrieved_utc": datetime.now(timezone.utc).isoformat(), "files": []}
    for name, url in SOURCES.items():
        payload = fetch(url)
        path = OUT / name
        path.write_bytes(payload)
        manifest["files"].append({"name": name, "url": url, "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()})
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"wrote {len(manifest['files'])} public metadata snapshots to {OUT}")


if __name__ == "__main__":
    main()
