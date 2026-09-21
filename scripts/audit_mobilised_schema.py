#!/usr/bin/env python3
"""Freeze a schema-only Mobilise-D release audit before inference."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.mobilised_cvs import audit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path, help="authorized extracted release directory")
    parser.add_argument("--output", type=Path, help="write JSON audit here")
    args = parser.parse_args()
    result = audit(args.root)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
