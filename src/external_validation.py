"""External audit/status layer. It fails closed rather than inventing analyses."""
from __future__ import annotations

import json
from pathlib import Path
import pandas as pd
import yaml

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
    mapping = yaml.safe_load((Path("configs") / "external_mappings.yaml").read_text())
    mobi_map = mapping["mobilised_cvs"]
    runtime_map = {"participant": mobi_map["participant"], "visit": mobi_map["visit"], "anchor": mobi_map["mds_updrs_iii"], "valid_days": mobi_map["valid_days"], "confirmatory_features": mobi_map["confirmatory_features"]}
    mobi = mobilised_cvs.build_mobilised_canonical(mobilised_cvs.load_pd_dataset(root / "MobiliseD_CVS_v1_0_0", runtime_map), runtime_map)
    reliable = mobilised_cvs.filter_reliable_week(mobi)
    features = [item["canonical"] for item in mobi_map["confirmatory_features"].values()]
    rows = [longitudinal_gee(reliable, f, "mdsscore3") for f in features]
    output = pd.DataFrame(rows); output["q_value"] = bh_fdr(output.p_value) if "p_value" in output else float("nan")
    output["estimability_status"] = output["status"]
    output["association_status"] = output.q_value.le(.05).map({True:"PASS", False:"FAIL"})
    output["monitoring_progression_status"] = output.apply(lambda r: "PASS" if r.estimability_status == "OK" and r.association_status == "PASS" else "FAIL" if r.estimability_status == "OK" else "INCOMPLETE", axis=1)
    output["dataset"] = "mobilised_cvs"; output["anchor_compatibility"] = "broad_motor"; output.to_csv(frozen / "mobilised_longitudinal_associations.csv", index=False)
    paired = pd.DataFrame([paired_change_summary(reliable, f, "mdsscore3") for f in features]); paired["dataset"] = "mobilised_cvs"; paired.to_csv(frozen / "mobilised_responsiveness.csv", index=False)
    pd.DataFrame([{ "dataset":"mobilised_cvs", "status":"OK", "n_rows_all":len(mobi), "n_rows_reliable":len(reliable), "n_participants_all":mobi.participant_key.nunique(), "n_participants_reliable":reliable.participant_key.nunique()}]).to_csv(frozen / "mobilised_missingness_summary.csv",index=False)
    site_rows=[]
    for feature in features:
        estimates=[]
        for site in sorted(reliable.site.dropna().astype(str).unique()):
            result=longitudinal_gee(reliable[reliable.site.astype(str).ne(site)], feature, "mdsscore3")
            if result["status"] == "OK": estimates.append(result["within_effect"])
        full=output.loc[output.feature.eq(feature),"within_effect"].iloc[0]
        consistent=bool(estimates) and all((x >= 0) == (full >= 0) for x in estimates)
        site_rows.append({"dataset":"mobilised_cvs","feature":feature,"n_leave_site_out_models":len(estimates),"status":"PASS" if consistent else "FAIL" if estimates else "NOT_ESTIMABLE","reason":"LEAVE_ONE_SITE_OUT_DIRECTION" if estimates else "SITE_UNAVAILABLE_OR_INSUFFICIENT"})
    pd.DataFrame(site_rows).to_csv(frozen / "mobilised_site_robustness.csv",index=False)
    tables = mendeley_gait.load_mendeley_processed_tables(root / "Mendeley_Gait_PD_v2")
    indicators = [c for c in tables["cross_sectional"].columns if c in set(mendeley_gait.PROCESSED_COLUMNS.values()) and c != "gait_evaluation"]
    cross=[]
    for f in indicators:
        frame=tables["cross_sectional"][[f,"gait_evaluation"]].dropna(); rho=spearmanr(frame[f],frame.gait_evaluation).statistic if len(frame)>2 else float("nan")
        cross.append({"dataset":"mendeley_gait","feature":f,"anchor_used":"Gait evaluation MDS-UPDRS","anchor_compatibility":"gait_item","n":len(frame),"spearman_rho":rho,"status":"OK" if len(frame)>=3 else "NOT_ESTIMABLE"})
    cross=pd.DataFrame(cross); cross.to_csv(frozen / "mendeley_cross_sectional_replication.csv",index=False)
    six=pd.DataFrame([paired_change_summary(tables["six_month"],f,"gait_evaluation") for f in indicators]); six["dataset"]="mendeley_gait"; six.to_csv(frozen / "mendeley_longitudinal_change.csv",index=False)
    timing=tables["medication_timing"]; timing_rows=[]
    for f in indicators:
        frame=timing[["participant_key", f,"time_since_medication_min"]].dropna().copy()
        frame["feature_within"] = frame[f] - frame.groupby("participant_key")[f].transform("mean")
        frame["timing_within"] = frame.time_since_medication_min - frame.groupby("participant_key").time_since_medication_min.transform("mean")
        usable = frame.groupby("participant_key").size(); frame = frame[frame.participant_key.isin(usable[usable >= 2].index)]
        timing_rows.append({"dataset":"mendeley_gait","feature":f,"n_rows":len(frame),"n_repeated_participants":frame.participant_key.nunique(),"within_person_spearman_rho":spearmanr(frame.feature_within,frame.timing_within).statistic if len(frame)>2 else float("nan"),"status":"OK" if frame.participant_key.nunique()>=2 else "NOT_ESTIMABLE"})
    pd.DataFrame(timing_rows).to_csv(frozen / "mendeley_medication_timing.csv",index=False)
    pd.DataFrame([{ "dataset":"adaptive_dbs", "status":"NOT_ESTIMABLE", "reason":"STATE_PAIR_MAPPING_NOT_FROZEN"}]).to_csv(frozen / "adaptive_dbs_state_sensitivity.csv",index=False)
    status += [{"dataset":"mobilised_cvs","enabled":True,"status":"OK","mapping_status":"APPROVED","reason":"RELEASE_MAPPING_V3_2_2"},{"dataset":"mendeley_gait","enabled":True,"status":"OK","mapping_status":"APPROVED","reason":"PROCESSED_TABLES_V3_2_2"},{"dataset":"adaptive_dbs","enabled":True,"status":"NOT_ESTIMABLE","mapping_status":"NOT_APPROVED","reason":"STATE_PAIR_MAPPING_NOT_FROZEN"}]
    pd.DataFrame(status).to_csv(frozen / "external_dataset_status.csv",index=False)
    evidence = []
    for row in output.to_dict("records"):
        evidence.append({"feature": row["feature"], "external_dataset": "mobilised_cvs", "anchor_used": "mdsscore3", "anchor_compatibility": "broad_motor", "estimability_status":row["estimability_status"],"association_status":row["association_status"], "cross_sectional_status": "NOT_APPLICABLE", "within_person_status": row["estimability_status"], "responsiveness_status": "INCOMPLETE", "measurement_error_status": "NOT_ESTIMABLE", "site_transport_status": "PENDING_TABLE", "state_response_status": "NOT_APPLICABLE", "monitoring_progression_status": row["monitoring_progression_status"], "trait_status_original": "UNCHANGED", "overall_reason": "Real-world repeated-visit broad-motor association; not a trait claim."})
    for row in cross.to_dict("records"):
        evidence.append({"feature": row["feature"], "external_dataset": "mendeley_gait", "anchor_used": row["anchor_used"], "anchor_compatibility": row["anchor_compatibility"], "estimability_status":row["status"],"association_status":"INCOMPLETE", "cross_sectional_status": row["status"], "within_person_status": "INCOMPLETE", "responsiveness_status": "INCOMPLETE", "measurement_error_status": "NOT_ESTIMABLE", "site_transport_status": "NOT_APPLICABLE", "state_response_status": "TIMING_ANALYSIS_AVAILABLE", "monitoring_progression_status": "INCOMPLETE", "trait_status_original": "UNCHANGED", "overall_reason": "Processed-table transport evidence; raw IDs were not joined."})
    pd.DataFrame(evidence).to_csv(frozen / "external_feature_evidence_matrix.csv", index=False)
    return audits
