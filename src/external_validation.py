"""External audit/status layer. It fails closed rather than inventing analyses."""
from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

from . import mendeley_gait, mobilised_cvs, adaptive_dbs
from .longitudinal_stats import longitudinal_gee, paired_change_summary
from .stats import bh_fdr
from scipy.stats import spearmanr


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


def run_external_analysis(root: Path, frozen: Path, config: dict) -> dict:
    """Execute approved, archive-native external analyses; write aggregates only."""
    audits = run_external_audits(root, frozen, config)
    status = []
    mobi = mobilised_cvs.build_mobilised_canonical(mobilised_cvs.load_pd_dataset(root / "MobiliseD_CVS_v1_0_0"))
    reliable = mobilised_cvs.filter_reliable_week(mobi)
    features = list(mobilised_cvs.RELEASE_MAPPING["features"].values())
    rows = [longitudinal_gee(reliable, f, "mdsscore3") for f in features]
    output = pd.DataFrame(rows); output["q_value"] = bh_fdr(output.p_value) if "p_value" in output else float("nan")
    output["dataset"] = "mobilised_cvs"; output["anchor_compatibility"] = "broad_motor"; output.to_csv(frozen / "mobilised_longitudinal_associations.csv", index=False)
    paired = pd.DataFrame([paired_change_summary(reliable, f, "mdsscore3") for f in features]); paired["dataset"] = "mobilised_cvs"; paired.to_csv(frozen / "mobilised_responsiveness.csv", index=False)
    pd.DataFrame([{ "dataset":"mobilised_cvs", "status":"OK", "n_rows_all":len(mobi), "n_rows_reliable":len(reliable), "n_participants_all":mobi.participant_key.nunique(), "n_participants_reliable":reliable.participant_key.nunique()}]).to_csv(frozen / "mobilised_missingness_summary.csv",index=False)
    pd.DataFrame([{ "dataset":"mobilised_cvs", "status":"NOT_ESTIMABLE", "reason":"SITE_SENSITIVITY_NOT_YET_IMPLEMENTED"}]).to_csv(frozen / "mobilised_site_robustness.csv",index=False)
    tables = mendeley_gait.load_mendeley_processed_tables(root / "Mendeley_Gait_PD_v2")
    indicators = [c for c in tables["cross_sectional"].columns if c in set(mendeley_gait.PROCESSED_COLUMNS.values())]
    cross=[]
    for f in indicators:
        frame=tables["cross_sectional"][[f,"gait_evaluation"]].dropna(); rho=spearmanr(frame[f],frame.gait_evaluation).statistic if len(frame)>2 else float("nan")
        cross.append({"dataset":"mendeley_gait","feature":f,"anchor_used":"Gait evaluation MDS-UPDRS","anchor_compatibility":"gait_item","n":len(frame),"spearman_rho":rho,"status":"OK" if len(frame)>=3 else "NOT_ESTIMABLE"})
    cross=pd.DataFrame(cross); cross.to_csv(frozen / "mendeley_cross_sectional_replication.csv",index=False)
    six=pd.DataFrame([paired_change_summary(tables["six_month"],f,"gait_evaluation") for f in indicators]); six["dataset"]="mendeley_gait"; six.to_csv(frozen / "mendeley_longitudinal_change.csv",index=False)
    timing=tables["medication_timing"]; timing_rows=[]
    for f in indicators:
        frame=timing[[f,"time_since_medication_min"]].dropna(); timing_rows.append({"dataset":"mendeley_gait","feature":f,"n":len(frame),"spearman_rho":spearmanr(frame[f],frame.time_since_medication_min).statistic if len(frame)>2 else float("nan"),"status":"OK" if len(frame)>=3 else "NOT_ESTIMABLE"})
    pd.DataFrame(timing_rows).to_csv(frozen / "mendeley_medication_timing.csv",index=False)
    pd.DataFrame([{ "dataset":"adaptive_dbs", "status":"NOT_ESTIMABLE", "reason":"STATE_PAIR_MAPPING_NOT_FROZEN"}]).to_csv(frozen / "adaptive_dbs_state_sensitivity.csv",index=False)
    status += [{"dataset":"mobilised_cvs","enabled":True,"status":"OK","mapping_status":"APPROVED","reason":"RELEASE_MAPPING_V3_2_2"},{"dataset":"mendeley_gait","enabled":True,"status":"OK","mapping_status":"APPROVED","reason":"PROCESSED_TABLES_V3_2_2"},{"dataset":"adaptive_dbs","enabled":True,"status":"NOT_ESTIMABLE","mapping_status":"NOT_APPROVED","reason":"STATE_PAIR_MAPPING_NOT_FROZEN"}]
    pd.DataFrame(status).to_csv(frozen / "external_dataset_status.csv",index=False)
    return audits
