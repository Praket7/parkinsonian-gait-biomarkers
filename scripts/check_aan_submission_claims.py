#!/usr/bin/env python3
"""Check AAN submission values against committed frozen aggregate outputs."""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALUES = ROOT / "report" / "AAN_submission_values.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def number(row: dict[str, str], key: str) -> float:
    return float(row[key])


def close(actual: float, expected: float, name: str, failures: list[str]) -> None:
    if not math.isclose(actual, expected, rel_tol=1e-8, abs_tol=1e-10):
        failures.append(f"{name}: expected {expected}, found {actual}")


def check_values(root: Path = ROOT) -> list[str]:
    values = json.loads((root / VALUES.relative_to(ROOT)).read_text(encoding="utf-8"))
    sources = values["source_files"]
    failures: list[str] = []

    primary_rows = read_csv(root / sources["primary"])
    primary = next(row for row in primary_rows if row["feature"] == "context_adjusted_gait_deviation_v1")
    for key, column in (
        ("standardized_effect", "effect"), ("ci_low", "ci_low"),
        ("ci_high", "ci_high"), ("q_value", "q_value"),
        ("speed_adjusted_effect", "speed_adjusted_effect"),
        ("speed_adjusted_ci_low", "speed_adjusted_ci_low"),
        ("speed_adjusted_ci_high", "speed_adjusted_ci_high"),
        ("speed_adjusted_q_value", "speed_adjusted_q_value"),
    ):
        close(number(primary, column), values["primary"][key], f"primary.{key}", failures)
    if int(primary["n_participants"]) != values["primary"]["n_participants"]:
        failures.append("primary participant count differs from frozen table")
    if int(primary["n_rows"]) != values["primary"]["score_association_rows"]:
        failures.append("score-association row count differs from frozen table")

    boot = read_csv(root / sources["reference_bootstrap"])
    same_direction = sum(float(row["direction"]) > 0 for row in boot) / len(boot)
    close(float(len(boot)), values["reference_robustness"]["resamples"], "reference resamples", failures)
    close(same_direction, values["reference_robustness"]["same_direction_fraction"], "reference direction fraction", failures)
    close(float(__import__("statistics").median(float(row["effect"]) for row in boot)),
          values["reference_robustness"]["median_standardized_effect"], "reference median", failures)

    repeated = read_csv(root / sources["h2_repeated"])
    participant = [row for row in repeated if row["level"] == "participant"]
    rows = [row for row in repeated if row["level"] == "row"]
    h2 = values["incremental_value"]
    close(float(len(participant)), h2["repeats"], "participant repeats", failures)
    close(float(sum(float(row["delta_spearman_rho"]) > 0 for row in participant) / len(participant)),
          h2["participant_spearman_favorable_fraction"], "participant rank fraction", failures)
    close(float(sum(float(row["delta_rmse"]) < 0 for row in participant) / len(participant)),
          h2["participant_rmse_favorable_fraction"], "participant RMSE fraction", failures)
    close(float(sum(float(row["delta_pearson_r"]) > 0 for row in participant) / len(participant)),
          h2["participant_pearson_favorable_fraction"], "participant Pearson fraction", failures)
    close(float(sum(abs(float(row["extended_calibration_slope"]) - 1) < abs(float(row["baseline_calibration_slope"]) - 1)
                    for row in participant) / len(participant)),
          h2["participant_calibration_slope_closer_to_one_fraction"], "participant slope calibration fraction", failures)
    close(float(sum(abs(float(row["extended_calibration_intercept"])) < abs(float(row["baseline_calibration_intercept"]))
                    for row in participant) / len(participant)),
          h2["participant_calibration_intercept_closer_to_zero_fraction"], "participant intercept calibration fraction", failures)
    close(float(sum(float(row["delta_spearman_rho"]) > 0 for row in rows) / len(rows)),
          h2["row_spearman_favorable_fraction"], "row rank fraction", failures)
    for level, source_column, target in (
        ("participant", "delta_spearman_rho", "participant_median_delta_spearman"),
        ("participant", "delta_rmse", "participant_median_delta_rmse"),
        ("participant", "delta_pearson_r", "participant_median_delta_pearson"),
        ("row", "delta_spearman_rho", "row_median_delta_spearman"),
    ):
        sample = participant if level == "participant" else rows
        median = __import__("statistics").median(float(row[source_column]) for row in sample)
        close(float(median), h2[target], target, failures)

    bridge = read_csv(root / sources["bridge"])
    if len(bridge) != values["analytical_bridge"]["features"] or any(row["analytic_equivalence_status"] != "PASS" for row in bridge):
        failures.append("analytical bridge does not show eight passing features")
    if {int(row["n"]) for row in bridge} != {values["analytical_bridge"]["matched_trials"]}:
        failures.append("analytical bridge trial count differs from frozen outputs")

    point = read_csv(root / sources["longitudinal_point"])
    intervals = read_csv(root / sources["longitudinal_ci"])
    for task, value in (("SelfPace", values["longitudinal_stability"]["self_pace"]),
                        ("HurriedPace", values["longitudinal_stability"]["hurried_pace"])):
        p = next(row for row in point if row["task"] == task)
        ci = next(row for row in intervals if row["task"] == task)
        close(float(p["icc_a1"]), value["icc"], f"{task} ICC", failures)
        close(float(ci["icc_bca_ci_low"]), value["bca_ci_low"], f"{task} BCa lower CI", failures)
        close(float(ci["icc_bca_ci_high"]), value["bca_ci_high"], f"{task} BCa upper CI", failures)
        if int(p["n_participants"]) != value["n"] or p["test_retest_status"] != value["status"]:
            failures.append(f"{task} longitudinal status/count differs from frozen outputs")
    return failures


if __name__ == "__main__":
    errors = check_values()
    if errors:
        raise SystemExit("\n".join(errors))
    print("AAN frozen-value consistency passed")
