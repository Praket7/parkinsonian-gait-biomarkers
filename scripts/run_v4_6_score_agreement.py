#!/usr/bin/env python3
"""Validate final frozen-score agreement between PKMAS and raw reconstruction."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import yaml

from check_v4_6_freeze import check
from src.v4_1.normative import load_frozen_model
from src.v4_6.score_agreement import score_agreement, score_matched_trials
from src.weargait_clinical import load_v1_clinical


def _clinical_covariates(v1_root: Path) -> pd.DataFrame:
    clinical = load_v1_clinical(
        v1_root / "PD - Demographic+Clinical - datasetV1.csv",
        v1_root / "CONTROLS - Demographic+Clinical - datasetV1.csv",
    )
    clinical = clinical.rename(columns={"participant_id": "participant"})
    if clinical.participant.duplicated().any():
        raise ValueError("V1 clinical participant IDs are not unique")
    return clinical[["participant", "age", "height_m"]]


def _update_summary(path: Path, metrics: dict) -> None:
    current = json.loads(path.read_text()) if path.exists() else {}
    current.setdefault("historical_score", {"status": "UNCHANGED", "longitudinal_interval": "six_plus_months"})
    current["score_level_analytical_agreement"] = metrics
    current.setdefault("claim_boundaries", {
        "short_term_reliability": "NOT_ESTIMABLE",
        "clinical_responsiveness": "NOT_ESTIMABLE",
        "external_full_score_transport": "NOT_ESTIMABLE",
    })
    path.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v1-root", required=True, type=Path)
    parser.add_argument("--input", type=Path, default=None, help="controlled local v4.3 matched feature table")
    parser.add_argument("--config", type=Path, default=Path("configs/v4_6_analysis.yaml"))
    parser.add_argument("--model", type=Path, default=Path("results/v4_1/frozen/v4_1_control_model.json"))
    parser.add_argument("--output", type=Path, default=Path("results/v4_6"))
    args = parser.parse_args()
    failures = check()
    if failures:
        raise SystemExit("\n".join(failures))
    config = yaml.safe_load(args.config.read_text())
    source = args.input or Path(config["v1_reconstructed_features_local"])
    if not source.exists():
        raise SystemExit(f"controlled local matched reconstruction table is unavailable: {source}")
    qc = json.loads(Path(config["v1_reconstruction_qc"]).read_text())
    if not qc.get("all_eight_equivalent"):
        raise SystemExit("v4.3 eight-input reconstruction bridge must pass before score-level analysis")
    matched = pd.read_csv(source)
    for name in ("age", "height_m"):
        if name in matched:
            matched = matched.drop(columns=[name])
    matched = matched.merge(_clinical_covariates(args.v1_root), on="participant", how="left", validate="many_to_one")
    if matched[["age", "height_m"]].isna().any().any():
        raise SystemExit("matched reconstruction rows are missing verified V1 age/height covariates")
    model = load_frozen_model(args.model)
    pairs = score_matched_trials(matched, model)
    metrics = score_agreement(pairs.score_pkmas.to_numpy(), pairs.score_raw.to_numpy())
    historical = pd.read_csv(config["v45_longitudinal_source"])
    comparison = historical[["task", "n_paired", "session_difference_sd"]].copy()
    comparison["score_agreement_rmse"] = metrics["rmse"]
    comparison["score_agreement_mae"] = metrics["mae"]
    comparison["rmse_to_between_visit_difference_sd"] = comparison.score_agreement_rmse / comparison.session_difference_sd
    comparison["interpretation"] = "Descriptive scale comparison only; not a test that analytical error is negligible"
    args.output.mkdir(parents=True, exist_ok=True)
    pairs.to_csv(args.output / "score_agreement_pairs_local.csv", index=False)
    pd.DataFrame([metrics]).to_csv(args.output / "score_agreement_summary.csv", index=False)
    comparison.to_csv(args.output / "score_vs_long_interval_scale.csv", index=False)
    (args.output / "score_agreement_summary.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    _update_summary(args.output / "v4_6_summary.json", metrics)


if __name__ == "__main__":
    main()
