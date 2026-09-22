#!/usr/bin/env python3
"""Apply the frozen V4.1 score to reconstructed longitudinal WearGait trials."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from run_v4_3_v1_equivalence import icc_a1
from src.v4_1.normative import score
from src.v4_3.walkway_reconstruction import FEATURES, reconstruct_csv


def clinical_covariates(v1_root: Path) -> pd.DataFrame:
    frame = pd.read_csv(v1_root / "PD - Demographic+Clinical - datasetV1.csv", header=1)
    frame = frame.rename(columns={"Subject ID": "participant", "Age (years)": "age", "Height (in)": "height_in"})
    frame["participant"] = frame.participant.astype(str).str.strip()
    frame["age"] = pd.to_numeric(frame.age, errors="coerce")
    frame["height_m"] = pd.to_numeric(frame.height_in, errors="coerce") * 0.0254
    return frame[["participant", "age", "height_m"]].dropna().drop_duplicates("participant")


def longitudinal_files(root: Path):
    directory = root / "PD Participants" / "00-CSV files"
    for task in ("SelfPace", "HurriedPace"):
        yield from directory.glob(f"*s[12]_{task}.csv")


def bootstrap_icc(first: np.ndarray, second: np.ndarray, seed: int = 20260922, n: int = 2000) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    values = np.asarray([icc_a1(first[index], second[index]) for index in rng.integers(0, len(first), size=(n, len(first)))])
    return tuple(np.quantile(values, [0.025, 0.975]).tolist())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v1-root", required=True, type=Path)
    parser.add_argument("--longitudinal-root", required=True, type=Path)
    parser.add_argument("--model", default="results/v4_1/frozen/v4_1_control_model.json", type=Path)
    parser.add_argument("--v1-qc", default="results/v4_3/v1_reconstruction_qc.json", type=Path)
    parser.add_argument("--output", default="results/v4_3", type=Path)
    parser.add_argument("--reconstructed", type=Path, help="optional precomputed raw-feature table")
    args = parser.parse_args()
    if not json.loads(args.v1_qc.read_text())["all_eight_equivalent"]:
        raise SystemExit("V1 analytical-equivalence gate failed")
    model = json.loads(args.model.read_text())
    model["features"] = model.pop("feature_order")
    model["beta"] = np.asarray(model["beta"])
    model["covariance"] = np.asarray(model["covariance"])
    if args.reconstructed:
        reconstructed, exclusions = pd.read_csv(args.reconstructed), []
    else:
        rows, exclusions = [], []
        expression = re.compile(r"(?P<participant>.+?)s(?P<session>[12])_(?P<task>SelfPace|HurriedPace)$")
        for path in longitudinal_files(args.longitudinal_root):
            match = expression.fullmatch(path.stem)
            if not match:
                continue
            try:
                rows.append({**match.groupdict(), "source_file": str(path), **reconstruct_csv(str(path))})
            except (ValueError, pd.errors.ParserError) as error:
                exclusions.append({**match.groupdict(), "source_file": str(path), "reason": str(error)})
        reconstructed = pd.DataFrame(rows)
    reconstructed["session"] = reconstructed.session.astype(str)
    reconstructed = reconstructed.merge(clinical_covariates(args.v1_root), on="participant", how="left")
    valid = reconstructed.dropna(subset=["age", "height_m", *FEATURES]).copy()
    metric_columns = ("gait_speed", "step_length_mean", "stride_length_mean")
    valid.loc[:, metric_columns] = valid.loc[:, metric_columns] / 100.0
    valid["context_adjusted_gait_deviation_v1"] = score(valid, model)
    records = []
    for task, group in valid.groupby("task"):
        paired = group.pivot_table(index="participant", columns="session", values="context_adjusted_gait_deviation_v1", aggfunc="first").dropna()
        first, second = paired["1"].to_numpy(), paired["2"].to_numpy()
        lower, upper = bootstrap_icc(first, second)
        records.append({"task": task, "estimability_status": "OK", "n_participants": len(paired), "icc_a1": icc_a1(first, second), "icc_a1_ci_low": lower, "icc_a1_ci_high": upper, "mean_change_s2_minus_s1": float(np.mean(second - first)), "mae": float(np.mean(abs(second - first))), "test_retest_status": "PASS" if lower >= 0.80 else "FAIL"})
    args.output.mkdir(parents=True, exist_ok=True)
    reconstructed.to_csv(args.output / "longitudinal_reconstructed_features.csv", index=False)
    pd.DataFrame(exclusions).to_csv(args.output / "longitudinal_reconstruction_exclusions.csv", index=False)
    pd.DataFrame(records).to_csv(args.output / "normative_longitudinal_stability.csv", index=False)
    (args.output / "h4_qc.json").write_text(json.dumps({
        "protocol": "v4.3.0", "model_refit": False, "model_source": str(args.model),
        "v1_bridge": "PASS", "reconstructed_trials": int(len(reconstructed)), "scored_trials": int(len(valid)),
        "excluded_trials": int(len(exclusions)), "h4_status": "ESTIMABLE",
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()

