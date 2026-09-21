import argparse
import json
import os
from pathlib import Path
import numpy as np
import pandas as pd

from .config import load_config
from .features import FEATURE_REGISTRY, aggregate_bouts
from .io import load_csv_bouts
from .stats import (adjusted_associations, participant_bootstrap_direction,
                    reliability_icc, variance_decomposition, within_person_changes)


def _feature_table(raw):
    """Support canonical pre-derived CSVs while preserving raw input columns."""
    expected = set(FEATURE_REGISTRY)
    present = expected & set(raw.columns)
    if not present:
        raise ValueError("input CSVs must contain derived feature columns or be adapted to the bout API")
    keep = [c for c in ["participant_id", "site", "session_id", "task", "mds_updrs_iii", "mds_updrs_gait_item", "age", "sex", "height_m", "medication_state", "time_since_medication", "disease_duration", "dbs_status"] if c in raw]
    return aggregate_bouts(pd.concat([raw[keep], raw[list(present)]], axis=1))


def _primary_severity(table):
    """Choose the prespecified gait item only when it has usable observations."""
    for name in ("mds_updrs_gait_item", "mds_updrs_iii"):
        if name in table and table[name].notna().sum() >= 12:
            return name
    return None


def run(config_path, data_root=None):
    config = load_config(config_path)
    np.random.seed(config["seed"])
    data = config["data"]
    authorized_root = data_root or os.environ.get("PARKINSON_GAIT_DATA_ROOT")
    if authorized_root:
        from .final_analysis import run_authorized_analysis
        return run_authorized_analysis(authorized_root, data.get("output_dir", "results"), config=config)
    raw = load_csv_bouts(data["input_dir"], data.get("file_glob", "*.csv"))
    outdir = Path(data.get("output_dir", "results"))
    outdir.mkdir(parents=True, exist_ok=True)
    if raw.empty:
        table = pd.DataFrame()
    else:
        table = _feature_table(raw)
    table.to_csv(outdir / "participant_task_features.csv", index=False)
    severity = _primary_severity(table)
    eligible = severity is not None
    associations = adjusted_associations(table, list(FEATURE_REGISTRY), severity) if eligible else pd.DataFrame(columns=["feature", "n", "effect", "ci_low", "ci_high", "p_value", "q_value"])
    if eligible:
        associations["direction_consistency"] = participant_bootstrap_direction(table, list(FEATURE_REGISTRY), severity, config["bootstrap_iterations"], config["seed"]).reindex(associations.feature).to_numpy()
    associations.to_csv(outdir / "primary_associations.csv", index=False)
    features = [f for f in FEATURE_REGISTRY if f in table]
    variance = variance_decomposition(table, features) if not table.empty else pd.DataFrame()
    variance.to_csv(outdir / "variance_decomposition.csv", index=False)
    reliability = reliability_icc(table, features) if not table.empty else pd.DataFrame()
    reliability.to_csv(outdir / "reliability.csv", index=False)
    longitudinal = within_person_changes(table, features, severity) if eligible else pd.DataFrame()
    longitudinal.to_csv(outdir / "longitudinal_changes.csv", index=False)
    trait = []
    state = []
    context = []
    if eligible and not associations.empty:
        for row in associations.itertuples():
            if pd.notna(row.q_value) and row.q_value <= config.get("fdr_alpha", 0.05) and getattr(row, "direction_consistency", 0) >= config.get("stability", {}).get("minimum_direction_consistency", 0.8):
                trait.append(row.feature)
    if not variance.empty:
        for row in variance.itertuples():
            if pd.notna(getattr(row, "task_fraction", np.nan)) and row.task_fraction >= 0.25:
                context.append(row.feature)
    manifest = {
        "analysis_version": config.get("analysis_version", "1.0"),
        "seed": config["seed"],
        "primary_n_participants": int(table["participant_id"].nunique()) if not table.empty else 0,
        "n_rows": int(len(table)),
        "primary_features": [f for f in FEATURE_REGISTRY if f in table],
        "trait_features": trait, "state_features": state, "context_features": context,
        "external_replication": {}, "longitudinal": {"status": "computed" if not longitudinal.empty else "not_estimable"},
        "status": "no_input_data" if raw.empty else ("feature_table_ready" if not eligible else "primary_associations_ready"),
        "primary_target": severity if eligible else None,
        "conclusion": "No hypothesis test was run: authorized participant-level data are unavailable." if raw.empty else ("Candidate trait features were identified under the frozen criteria." if trait else "No candidate trait features met the frozen criteria."),
    }
    (outdir / "frozen").mkdir(exist_ok=True)
    (outdir / "frozen" / "results.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main():
    parser = argparse.ArgumentParser(description="Run the reproducible gait feature pipeline")
    parser.add_argument("--config", default="configs/analysis.yaml")
    parser.add_argument("--data-root", help="Authorized local Drive folder containing the three releases")
    args = parser.parse_args()
    print(json.dumps(run(args.config, args.data_root), indent=2))


if __name__ == "__main__":
    main()
