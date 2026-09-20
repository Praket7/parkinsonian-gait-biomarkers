import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

from .config import load_config
from .features import FEATURE_REGISTRY, aggregate_bouts
from .io import load_csv_bouts
from .stats import adjusted_associations, participant_bootstrap_direction


def _feature_table(raw):
    """Support canonical pre-derived CSVs while preserving raw input columns."""
    expected = set(FEATURE_REGISTRY)
    present = expected & set(raw.columns)
    if not present:
        raise ValueError("input CSVs must contain derived feature columns or be adapted to the bout API")
    keep = [c for c in ["participant_id", "site", "session_id", "task", "mds_updrs_iii", "mds_updrs_gait_item", "age", "sex", "height_m"] if c in raw]
    return aggregate_bouts(pd.concat([raw[keep], raw[list(present)]], axis=1))


def run(config_path):
    config = load_config(config_path)
    np.random.seed(config["seed"])
    data = config["data"]
    raw = load_csv_bouts(data["input_dir"], data.get("file_glob", "*.csv"))
    outdir = Path(data.get("output_dir", "results"))
    outdir.mkdir(parents=True, exist_ok=True)
    if raw.empty:
        table = pd.DataFrame()
    else:
        table = _feature_table(raw)
    table.to_csv(outdir / "participant_task_features.csv", index=False)
    severity = "mds_updrs_gait_item" if "mds_updrs_gait_item" in table else "mds_updrs_iii"
    eligible = not table.empty and severity in table and table[severity].notna().sum() >= 12
    associations = adjusted_associations(table, list(FEATURE_REGISTRY), severity) if eligible else pd.DataFrame(columns=["feature", "n", "effect", "ci_low", "ci_high", "p_value", "q_value"])
    if eligible:
        associations["direction_consistency"] = participant_bootstrap_direction(table, list(FEATURE_REGISTRY), severity, config["bootstrap_iterations"], config["seed"]).reindex(associations.feature).to_numpy()
    associations.to_csv(outdir / "primary_associations.csv", index=False)
    manifest = {
        "analysis_version": config.get("analysis_version", "1.0"),
        "seed": config["seed"],
        "primary_n_participants": int(table["participant_id"].nunique()) if not table.empty else 0,
        "n_rows": int(len(table)),
        "primary_features": [f for f in FEATURE_REGISTRY if f in table],
        "trait_features": [], "state_features": [], "context_features": [],
        "external_replication": {}, "longitudinal": {},
        "status": "no_input_data" if raw.empty else ("feature_table_ready" if not eligible else "primary_associations_ready"),
        "primary_target": severity if eligible else None,
        "conclusion": "No hypothesis test was run: authorized participant-level data are unavailable." if raw.empty else None,
    }
    (outdir / "frozen").mkdir(exist_ok=True)
    (outdir / "frozen" / "results.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main():
    parser = argparse.ArgumentParser(description="Run the reproducible gait feature pipeline")
    parser.add_argument("--config", default="configs/analysis.yaml")
    args = parser.parse_args()
    print(json.dumps(run(args.config), indent=2))


if __name__ == "__main__":
    main()
