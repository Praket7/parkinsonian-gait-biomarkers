#!/usr/bin/env python3
"""Schema-only audit for longitudinal WearGait files and Synapse metadata.

Only MAT/HDF5 headers, names, shapes, dtypes, attributes, and metadata text
are inspected.  No signal arrays, table rows, or participant values are read
or written to the report.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SEARCH_TERMS = (
    "mds", "updrs", "clinical", "score", "visit", "session", "subject",
    "participant", "medication", "dbs", "assessment",
)
_TERM_RE = re.compile("|".join(re.escape(term) for term in SEARCH_TERMS), re.I)
_ID_TERMS = ("participant", "subject", "session", "visit")
_CLINICAL_TERMS = ("mds", "updrs", "clinical", "score", "assessment")


def _hits(names: list[str]) -> list[str]:
    lowered = " ".join(names).lower()
    return sorted({term for term in SEARCH_TERMS if term in lowered})


def _safe_name(value: Any) -> str:
    """Stringify header metadata without dereferencing a value payload."""
    return str(value).replace("\n", " ")[:500]


def audit_mat(path: Path) -> dict[str, Any]:
    try:
        from scipy.io import whosmat
    except ImportError as exc:  # pragma: no cover - environment dependent
        return {"path": path.name, "format": "mat", "error": f"scipy unavailable: {exc}"}
    try:
        variables = whosmat(str(path))
        rows = [{"name": _safe_name(name), "shape": list(shape), "class": _safe_name(kind)}
                for name, shape, kind in variables]
        names = [row["name"] for row in rows]
        return {
            "path": path.name,
            "format": "mat",
            "variables": rows,
            "schema_keyword_hits": _hits(names),
            "participant_session_clinical_schema": _has_joinable_schema(names),
        }
    except Exception as exc:
        return {"path": path.name, "format": "mat", "error": type(exc).__name__}


def audit_hdf5(path: Path) -> dict[str, Any]:
    try:
        import h5py
    except ImportError as exc:  # pragma: no cover - environment dependent
        return {"path": path.name, "format": "hdf5", "error": f"h5py unavailable: {exc}"}
    entries: list[dict[str, Any]] = []
    try:
        with h5py.File(path, "r") as handle:
            def visit(name: str, obj: Any) -> None:
                # visititems exposes metadata only; never index/read obj data.
                attrs = sorted(str(key) for key in obj.attrs.keys())
                row: dict[str, Any] = {"name": name, "kind": "dataset" if isinstance(obj, h5py.Dataset) else "group",
                                       "attributes": attrs}
                if isinstance(obj, h5py.Dataset):
                    row.update({"shape": list(obj.shape), "dtype": str(obj.dtype)})
                entries.append(row)
            handle.visititems(visit)
        names = [str(row["name"]) for row in entries] + [a for row in entries for a in row["attributes"]]
        return {
            "path": path.name,
            "format": "hdf5",
            "entries": entries,
            "schema_keyword_hits": _hits(names),
            "participant_session_clinical_schema": _has_joinable_schema(names),
        }
    except Exception as exc:
        return {"path": path.name, "format": "hdf5", "error": type(exc).__name__}


def _has_joinable_schema(names: list[str]) -> bool:
    """Require identifier/session and clinical-score terms in the same schema."""
    lowered = " ".join(names).lower()
    has_id = any(term in lowered for term in _ID_TERMS)
    has_session = "session" in lowered or "visit" in lowered
    has_clinical = any(term in lowered for term in _CLINICAL_TERMS)
    return bool(has_id and has_session and has_clinical)


def audit_synapse_metadata(paths: list[Path]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    all_names: list[str] = []
    for path in paths:
        try:
            # Metadata/manifests are explicitly supplied by the acquisition
            # record.  Read text only; never follow entity file handles.
            text = path.read_text(encoding="utf-8", errors="replace")
            names = sorted(set(_TERM_RE.findall(text)))
            all_names.extend(names)
            rows.append({"path": path.name, "bytes": path.stat().st_size,
                         "sha256": hashlib.sha256(text.encode()).hexdigest(),
                         "metadata_keyword_hits": sorted({name.lower() for name in names}),
                         "participant_session_clinical_reference": _has_joinable_schema([text])})
        except (OSError, UnicodeError) as exc:
            rows.append({"path": path.name, "error": type(exc).__name__})
    return {"files": rows, "keyword_hits": sorted(set(all_names)),
            "participant_session_clinical_reference": any(row.get("participant_session_clinical_reference") for row in rows)}


def audit_archive(root: str | Path, metadata_paths: list[str | Path] = ()) -> dict[str, Any]:
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"archive directory not found: {root}")
    schema_rows: list[dict[str, Any]] = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        if path.suffix.lower() == ".mat":
            schema_rows.append(audit_mat(path))
        elif path.suffix.lower() in {".h5", ".hdf5"}:
            schema_rows.append(audit_hdf5(path))
    synapse = audit_synapse_metadata([Path(item).expanduser() for item in metadata_paths])
    found = any(row.get("participant_session_clinical_schema") for row in schema_rows) or synapse["participant_session_clinical_reference"]
    return {
        "archive": str(root),
        "schema_files": len(schema_rows),
        "schema_rows": schema_rows,
        "synapse_metadata": synapse,
        "joinable_participant_session_clinical_schema": bool(found),
        "longitudinal_clinical_status": "SCHEMA_REFERENCE_FOUND" if found else "NOT_ESTIMABLE_AFTER_ARCHIVE_AND_SCHEMA_AUDIT",
        "interpretation": "Clinical longitudinal validity could not be evaluated from the authorized release as obtained." if not found else "A candidate schema reference was found; validate keys before modeling.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--metadata", type=Path, action="append", default=[])
    parser.add_argument("--output", type=Path, default=Path("results/longitudinal_schema_audit.json"))
    args = parser.parse_args()
    report = audit_archive(args.archive, args.metadata)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("schema_files", "joinable_participant_session_clinical_schema", "longitudinal_clinical_status")}, sort_keys=True))


if __name__ == "__main__":
    main()
