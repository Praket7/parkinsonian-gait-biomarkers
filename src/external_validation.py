"""External audit/status layer. It fails closed rather than inventing analyses."""
from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

from . import mendeley_gait, mobilised_cvs, adaptive_dbs


def _public_audit(audit: dict) -> dict:
    """Keep source inventory and filenames out of the published result bundle."""
    allowed = {"dataset", "status", "reason", "n_source_members", "has_raw_signal",
               "has_pd", "has_control", "has_state_metadata", "has_gait_metadata",
               "mapping_required", "pd_dataset_present", "components", "missing_components",
               "participant_visit_key_unique", "source_members_are_not_published"}
    return {key: value for key, value in audit.items() if key in allowed}


def run_external_audits(root: Path, frozen: Path, config: dict) -> dict:
    adapters = {"mendeley_gait": (mendeley_gait.audit, "Mendeley_Gait_PD_v2"),
                "mobilised_cvs": (mobilised_cvs.audit, "MobiliseD_CVS_v1_0_0"),
                "adaptive_dbs": (adaptive_dbs.audit, "AdaptiveDBS_Gait_2026")}
    audits, status_rows = {}, []
    for name, (audit, folder) in adapters.items():
        enabled = bool(config.get("external_data", {}).get(name, {}).get("enabled", False))
        result = audit(root / folder) if enabled else {"status": "DISABLED"}
        audits[name] = _public_audit(result)
        status_rows.append({"dataset": name, "enabled": enabled, "status": result["status"],
                            "reason": "SOURCE_PRESENT_MAPPING_NOT_APPROVED" if result["status"] == "OK" else "SOURCE_COMPONENT_MISSING"})
    (frozen / "external_schema_audit.json").write_text(json.dumps(audits, indent=2) + "\n")
    pd.DataFrame(status_rows).to_csv(frozen / "external_dataset_status.csv", index=False)
    # Required aggregate tables exist even before a reviewed source-variable
    # mapping has been approved.  They are intentionally final NOT_ESTIMABLE
    # statements, not provisional values that could be mistaken for evidence.
    placeholders = {"mendeley_cross_sectional_replication.csv":"mendeley_gait", "mendeley_longitudinal_change.csv":"mendeley_gait",
                    "mendeley_medication_timing.csv":"mendeley_gait", "mobilised_longitudinal_associations.csv":"mobilised_cvs",
                    "mobilised_responsiveness.csv":"mobilised_cvs", "mobilised_site_robustness.csv":"mobilised_cvs",
                    "mobilised_missingness_summary.csv":"mobilised_cvs", "adaptive_dbs_state_sensitivity.csv":"adaptive_dbs"}
    status = {row["dataset"]: row for row in status_rows}
    for filename, dataset in placeholders.items():
        row = status[dataset]
        pd.DataFrame([{"dataset":dataset,"status":"NOT_ESTIMABLE","reason":row["reason"]}]).to_csv(frozen / filename,index=False)
    pd.DataFrame([{"feature":"external","overall_measurement_class":"insufficient_evidence","overall_reason":"External source audits are not inferential evidence."}]).to_csv(frozen / "external_feature_evidence_matrix.csv", index=False)
    return audits
