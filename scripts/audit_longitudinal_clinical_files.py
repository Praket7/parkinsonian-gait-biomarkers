#!/usr/bin/env python3
"""Audit an authorized WearGait-PD Longitudinal archive without exporting values.

The output is file-level metadata only: paths relative to the supplied archive,
hashes, sizes, row/column counts, and safe key/keyword indicators.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

KEYWORDS = ("clinical", "demographic", "mds", "updrs", "score", "visit", "session", "follow", "participant", "subject")
PARTICIPANT_RE = re.compile(r"(?:NLS|WPD)\d+", re.I)
SESSION_RE = re.compile(r"s[12](?:\D|$)", re.I)
DEFAULT_MAX_HASH_BYTES = 50 * 1024 * 1024


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _csv_metadata(path: Path, *, count_rows: bool) -> tuple[int | None, list[str]]:
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader, [])
    # Files in this archive are row-oriented; counting physical records avoids
    # loading participant-level signal values into memory.
    rows = None
    if count_rows:
        with path.open("rb") as handle:
            rows = max(0, sum(1 for _ in handle) - 1)
    return rows, [str(value).strip() for value in header if str(value).strip()]


def audit_archive(root: str | Path, *, max_hash_bytes: int = DEFAULT_MAX_HASH_BYTES) -> list[dict[str, object]]:
    """Return public-safe metadata rows for every regular file below *root*."""
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"archive directory not found: {root}")
    rows: list[dict[str, object]] = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        relative = path.relative_to(root).as_posix()
        suffix = path.suffix.lower()
        columns: list[str] = []
        row_count: int | None = None
        if suffix in {".csv", ".tsv"}:
            row_count, columns = _csv_metadata(path, count_rows=path.stat().st_size <= max_hash_bytes)
        # MAT payloads are intentionally not loaded: this audit is about
        # discoverable filenames/headers and must not materialize signal data.
        names = [path.name, *columns]
        lowered = [name.lower() for name in names]
        filename_keyword_hits = sorted({keyword for keyword in KEYWORDS if keyword in path.name.lower()})
        header_keyword_hits = sorted({keyword for keyword in KEYWORDS if any(keyword in name for name in (column.lower() for column in columns))})
        keyword_hits = sorted(set(filename_keyword_hits) | set(header_keyword_hits))
        size_bytes = path.stat().st_size
        hashed = size_bytes <= max_hash_bytes
        rows.append({
            "relative_path": relative,
            "extension": suffix,
            "size_bytes": size_bytes,
            "sha256": _sha256(path) if hashed else "",
            "sha256_status": "complete" if hashed else "skipped_large_file",
            "row_count": row_count,
            "column_count": len(columns) if columns else None,
            "column_names": "|".join(columns),
            "keyword_hits": "|".join(keyword_hits),
            "filename_keyword_hits": "|".join(filename_keyword_hits),
            "header_keyword_hits": "|".join(header_keyword_hits),
            "participant_key_in_name": bool(PARTICIPANT_RE.search(path.name)),
            "session_key_in_name": bool(SESSION_RE.search(path.name)),
            "participant_key_in_header": any("participant" in name or "subject" in name for name in (c.lower() for c in columns)),
            "session_key_in_header": any("session" in name or "visit" in name or "follow" in name for name in (c.lower() for c in columns)),
        })
    return rows


def write_audit(rows: list[dict[str, object]], output: str | Path) -> None:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else ["relative_path"]
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--output", type=Path, default=Path("results/longitudinal_clinical_audit.csv"))
    parser.add_argument("--max-hash-bytes", type=int, default=DEFAULT_MAX_HASH_BYTES)
    args = parser.parse_args()
    rows = audit_archive(args.archive, max_hash_bytes=args.max_hash_bytes)
    write_audit(rows, args.output)
    clinical = [row for row in rows if row["keyword_hits"]]
    print(json.dumps({"files": len(rows), "keyword_hit_files": len(clinical), "output": str(args.output)}, sort_keys=True))


if __name__ == "__main__":
    main()
