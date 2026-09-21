#!/usr/bin/env python3
"""Write the content-addressed v4 protocol freeze before clinical inference."""
from __future__ import annotations
import hashlib, json, os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    files = [ROOT / "configs/v4_analysis.yaml", ROOT / "configs/v4_feature_definitions.yaml", ROOT / "configs/external_mappings.yaml",
             ROOT / "docs/v4_preregistration.md", *sorted((ROOT / "src/v4").glob("*.py")),
             *[ROOT / f"scripts/{name}" for name in ("run_v4_measurement_validation.py", "run_v4_primary_analysis.py", "run_v4_external_validation.py")]]
    manifest = {"schema": "v4-protocol-freeze-v1", "analysis_freeze_commit_sha": os.environ.get("V4_FREEZE_COMMIT", "UNAVAILABLE"),
                "files": {path.relative_to(ROOT).as_posix(): digest(path) for path in files}}
    output = ROOT / "results/v4/frozen/protocol_manifest.json"; output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2) + "\n"); print(output)


if __name__ == "__main__": main()
