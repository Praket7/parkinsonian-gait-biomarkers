#!/usr/bin/env python3
"""Validate documented raw-walkway reconstruction against V1 PKMAS exports."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.v4_2.analytical_equivalence import agreement
from src.v4_3.walkway_reconstruction import FEATURES, reconstruct_csv

PKMAS_COLUMNS = {
    "gait_speed": "Velocity (cm./sec.)",
    "cadence": "Cadence (steps/min.)",
    "step_length_mean": "Step Length (cm.)__Mean",
    "stride_length_mean": "Stride Length (cm.)__Mean",
    "step_time_mean": "Step Time (sec.)__Mean",
    "stride_time_mean": "Stride Time (sec.)__Mean",
    "step_time_cv": "Step Time (sec.)__%CV",
    "stride_time_cv": "Stride Time (sec.)__%CV",
}


def icc_a1(reference: np.ndarray, reconstruction: np.ndarray) -> float:
    values = np.column_stack((reference, reconstruction))
    n, k = values.shape
    row_means, column_means, mean = values.mean(axis=1), values.mean(axis=0), values.mean()
    ms_rows = k * np.square(row_means - mean).sum() / (n - 1)
    ms_columns = n * np.square(column_means - mean).sum() / (k - 1)
    residual = values - row_means[:, None] - column_means[None, :] + mean
    ms_error = np.square(residual).sum() / ((n - 1) * (k - 1))
    return float((ms_rows - ms_error) / (ms_rows + (k - 1) * ms_error + k * (ms_columns - ms_error) / n))


def truth_table(path: Path) -> pd.DataFrame:
    truth = pd.read_csv(path, header=[0, 1])
    truth.columns = ["__".join(str(part) for part in column if "Unnamed" not in str(part)).strip("_") for column in truth.columns]
    return truth[["Task", "Participant ID", *PKMAS_COLUMNS.values()]].rename(
        columns={"Task": "task", "Participant ID": "participant", **{source: target for target, source in PKMAS_COLUMNS.items()}}
    )


def raw_files(root: Path, wanted: set[tuple[str, str]]):
    for group in ("PD PARTICIPANTS", "CONTROL PARTICIPANTS"):
        for task in ("SelfPace", "HurriedPace"):
            for path in (root / group / "CSV files").glob(f"*_{task}.csv"):
                participant, file_task = path.stem.split("_", 1)
                if (participant, file_task) in wanted:
                    yield path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v1-root", required=True, type=Path)
    parser.add_argument("--output", default="results/v4_3", type=Path)
    args = parser.parse_args()
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    truth = truth_table(args.v1_root / "Walkway-derived metrics" / "PKMAS Walkway Gait Metrics - HP+SP.csv")
    truth["task"] = truth.task.astype(str).str.strip()
    truth["participant"] = truth.participant.astype(str).str.strip()
    reconstructed, exclusions = [], []
    for path in raw_files(args.v1_root, set(zip(truth.participant, truth.task))):
        participant, task = path.stem.split("_", 1)
        try:
            reconstructed.append({"participant": participant, "task": task, **reconstruct_csv(str(path))})
        except (ValueError, pd.errors.ParserError) as error:
            exclusions.append({"participant": participant, "task": task, "reason": str(error)})
    reconstructed_table = pd.DataFrame(reconstructed)
    merged = truth.merge(
        reconstructed_table, on=("participant", "task"), how="inner", suffixes=("_pkmas", "_raw")
    )
    rows, all_pass = [], True
    for feature in FEATURES:
        pair = merged[[f"{feature}_pkmas", f"{feature}_raw"]].apply(pd.to_numeric, errors="coerce").dropna()
        reference, raw = pair.iloc[:, 0].to_numpy(float), pair.iloc[:, 1].to_numpy(float)
        stats = agreement(reference, raw)
        stats["icc_a1"] = icc_a1(reference, raw)
        relative_bias = abs(stats["mean_bias"]) / abs(reference.mean())
        if feature.endswith("_cv"):
            passed = stats["icc_a1"] >= 0.85 and stats["ccc"] >= 0.85 and abs(stats["mean_bias"]) <= 2.0
        else:
            passed = stats["icc_a1"] >= 0.90 and stats["ccc"] >= 0.90 and relative_bias <= 0.05
        all_pass &= passed
        rows.append({"feature": feature, "estimability_status": "OK", "analytic_equivalence_status": "PASS" if passed else "FAIL", "relative_bias": relative_bias, **stats})
    pd.DataFrame(rows).to_csv(output / "v1_reconstruction_agreement.csv", index=False)
    pd.DataFrame(exclusions).to_csv(output / "v1_reconstruction_exclusions.csv", index=False)
    merged.to_csv(output / "v1_reconstructed_features.csv", index=False)
    (output / "v1_reconstruction_qc.json").write_text(json.dumps({
        "protocol": "v4.3.0", "coordinate_source": "WearGait-PD Supplementary Table S5 and Figure S5",
        "cell_pitch_cm": 1.27, "matched_trials": int(len(merged)), "excluded_raw_trials": int(len(exclusions)),
        "all_eight_equivalent": bool(all_pass), "h4_bridge_status": "PASS" if all_pass else "FAIL",
    }, indent=2) + "\n")
    if not all_pass:
        raise SystemExit("V1 analytical-equivalence gate failed; longitudinal H4 must remain not estimable.")


if __name__ == "__main__":
    main()

