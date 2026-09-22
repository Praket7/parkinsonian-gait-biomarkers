#!/usr/bin/env python3
"""Inventory authorized longitudinal anchors and CARE-PD measurement bridge."""
from __future__ import annotations

import argparse
import csv
import json
import re
import signal
import tempfile
from pathlib import Path

import pandas as pd
from scipy.io import loadmat, whosmat

from src.v4_1.normative import FEATURES


ANCHOR = re.compile(r"updrs|mds|medicat|levodopa|dose|\bdbs\b|clinical.?score", re.I)
SESSION = re.compile(r"(?P<participant>.+?)s(?P<session>[12])(?:_|$)")


def audit(longitudinal: Path, v1: Path, care: Path, hydrate_unreadable: bool = False) -> dict:
    base = longitudinal / "PD Participants"
    manifest = pd.read_csv(base / "manifest.csv", usecols=["name", "ID", "contentType"])
    csv_paths = sorted((base / "00-CSV files").glob("*.csv"))
    task = [path for path in csv_paths if re.search(r"s[12]_(SelfPace|HurriedPace)\.csv$", path.name)]
    mat_paths = sorted((base / "01-MAT files").glob("*s[12].mat"))
    if not csv_paths or not mat_paths:
        raise ValueError("longitudinal CSV and session MAT inventory required")
    headers, failed_csv = set(), []
    def timeout(*_):
        raise TimeoutError("cloud file did not open within five seconds")
    previous = signal.signal(signal.SIGALRM, timeout)
    for path in task:
        try:
            signal.setitimer(signal.ITIMER_REAL, 5)
            with path.open(newline="", encoding="utf-8", errors="replace") as handle:
                headers.add(tuple(next(csv.reader(handle))))
        except (OSError, StopIteration, TimeoutError) as error:
            failed_csv.append((path.name, type(error).__name__))
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
    signal.signal(signal.SIGALRM, previous)
    variables, fields, failed_mat, top_level_read, recovered_mat = set(), set(), [], 0, 0
    by_name = dict(zip(manifest.name.astype(str), manifest.ID.astype(str))) if "ID" in manifest else {}
    client = None
    workspace = tempfile.TemporaryDirectory(prefix="gait-v4-5-mat-") if hydrate_unreadable else None
    if hydrate_unreadable:
        import synapseclient
        client = synapseclient.Synapse(cache_root_dir=str(Path(workspace.name) / "cache"))
        client.login(silent=True)

    def inspect(path: Path) -> None:
        nonlocal top_level_read
        names = [name for name, _, _ in whosmat(path) if not name.startswith("__")]
        top_level_read += 1
        variables.update(names)
        structs = loadmat(path, variable_names=names, struct_as_record=False, squeeze_me=True)
        for item in structs.values():
            fields.update(getattr(item, "_fieldnames", []) or [])

    previous = signal.signal(signal.SIGALRM, timeout)
    for path in mat_paths:
        try:
            signal.setitimer(signal.ITIMER_REAL, 5)
            inspect(path)
        except (OSError, ValueError, NotImplementedError, TimeoutError) as error:
            signal.setitimer(signal.ITIMER_REAL, 0)
            if client is None or path.name not in by_name:
                failed_mat.append((path.name, type(error).__name__))
                continue
            try:
                fresh = Path(client.get(by_name[path.name], downloadLocation=workspace.name).path)
                inspect(fresh)
                recovered_mat += 1
                fresh.unlink()
            except (OSError, ValueError, NotImplementedError, TimeoutError) as retry_error:
                failed_mat.append((path.name, type(retry_error).__name__))
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
    signal.signal(signal.SIGALRM, previous)
    if workspace is not None:
        workspace.cleanup()
    v1_clinical = pd.read_csv(v1 / "PD - Demographic+Clinical - datasetV1.csv", header=1, usecols=["Subject ID"])
    v1_ids = set(v1_clinical["Subject ID"].dropna().astype(str).str.strip())
    sessions = {(m.group("participant"), m.group("session")) for path in task if (m := SESSION.match(path.stem))}
    matched_v1 = {sid for sid, session in sessions if session == "1" and sid in v1_ids}
    all_fields = set().union(*[set(item) for item in headers]) | variables | fields | set(manifest.columns)
    candidates = sorted(item for item in all_fields if ANCHOR.search(str(item)))
    named_sources = sorted(name for name in manifest.name.astype(str) if ANCHOR.search(name))
    explicit_anchor = [item for item in candidates if item.lower() != "clinicalevent"]
    care_files = sorted(path.name for path in care.glob("*.pkl"))
    return {
        "manifest_rows": len(manifest), "csv_files_inventoried": len(csv_paths), "task_csv_headers_read": len(task)-len(failed_csv),
        "distinct_csv_schemas": len(headers), "session_mat_files_inventoried": len(mat_paths),
        "session_mat_top_levels_read": top_level_read,
        "session_mat_structures_read": len(mat_paths)-len(failed_mat), "mat_top_level_variables": sorted(variables),
        "session_mat_recovered_from_synapse": recovered_mat,
        "mat_struct_fields": sorted(fields), "failed_csv_count": len(failed_csv), "failed_mat_count": len(failed_mat),
        "task_files": len(task), "unique_task_participant_sessions": len(sessions),
        "v1_participants_matching_session1_identifiers": len(matched_v1),
        "v1_linkage_status": "IDENTIFIER_OVERLAP_ONLY_NO_SESSION_DATE_EQUIVALENCE",
        "anchor_like_field_names": candidates, "manifest_anchor_like_filenames": named_sources,
        "explicit_repeated_clinical_anchor_fields": explicit_anchor,
        "clinical_audit_completeness": "INCOMPLETE" if failed_csv or failed_mat else "COMPLETE",
        "clinical_responsiveness_status": "NOT_ESTIMABLE" if not explicit_anchor and not named_sources else "REQUIRES_LINKAGE_AUDIT",
        "clinical_reason": "No verified session-specific MDS-UPDRS, dose timing, medication state or DBS variable in inspected schemas; "
                           + ("unreadable MAT structures are a coverage gap; " if failed_mat else "all session MAT structures were inspected; ")
                           + "ClinicalEvent is a task annotation stream, and V1 identifiers do not establish session-2 clinical anchors",
        "care_original_pickle_files": care_files,
        "care_eight_input_equivalence": {feature: "NOT_VALIDATED" for feature in FEATURES},
        "care_lodo_status": "NOT_ESTIMABLE_MEASUREMENT_BRIDGE_NOT_VALIDATED",
        "care_medication_response_status": "NOT_ESTIMABLE_FROZEN_SCORE_BRIDGE_NOT_VALIDATED",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", required=True, type=Path)
    parser.add_argument("--hydrate-unreadable", action="store_true", help="use fresh authorized Synapse copies for cloud placeholders")
    parser.add_argument("--output", type=Path, default=Path("results/v4_5"))
    args = parser.parse_args()
    result = audit(args.data_root / "WearGait_PD_Longitudinal", args.data_root / "WearGait_PD_V1", args.data_root / "CARE_PD", args.hydrate_unreadable)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "source_audit.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
