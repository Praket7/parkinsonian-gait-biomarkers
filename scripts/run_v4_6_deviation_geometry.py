#!/usr/bin/env python3
"""Run the prespecified v4.6 six-plus-month deviation-direction analysis."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from check_v4_6_freeze import check
from src.v4_1.normative import load_frozen_model
from src.v4_6.longitudinal_direction import (
    holm_adjust,
    pair_direction_rows,
    participant_bootstrap,
    permutation_null,
    plus_one_p_value,
)


def _update_summary(path: Path, direction: dict) -> None:
    current = json.loads(path.read_text()) if path.exists() else {}
    current.setdefault("historical_score", {"status": "UNCHANGED", "longitudinal_interval": "six_plus_months"})
    current["longitudinal_direction_conservation"] = direction
    current.setdefault("claim_boundaries", {
        "short_term_reliability": "NOT_ESTIMABLE",
        "clinical_responsiveness": "NOT_ESTIMABLE",
        "external_full_score_transport": "NOT_ESTIMABLE",
    })
    path.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=None, help="controlled local four-pass endpoint table")
    parser.add_argument("--config", type=Path, default=Path("configs/v4_6_analysis.yaml"))
    parser.add_argument("--model", type=Path, default=Path("results/v4_1/frozen/v4_1_control_model.json"))
    parser.add_argument("--output", type=Path, default=Path("results/v4_6"))
    args = parser.parse_args()
    failures = check()
    if failures:
        raise SystemExit("\n".join(failures))
    config = yaml.safe_load(args.config.read_text())
    source = args.input or Path(config["longitudinal_endpoints_local"])
    if not source.exists():
        raise SystemExit(f"controlled local longitudinal endpoint table is unavailable: {source}")
    endpoint = pd.read_csv(source, dtype={"session": str})
    spatial = [name for name in ("gait_speed", "step_length_mean", "stride_length_mean") if name in endpoint]
    endpoint.loc[:, spatial] = endpoint.loc[:, spatial].apply(pd.to_numeric, errors="coerce") / 100.0
    model = load_frozen_model(args.model)
    tasks = list(config["primary_tasks"])
    pairs = pair_direction_rows(endpoint, model, tasks=tasks)
    records, null_rows, raw_p = [], [], {}
    direction_summary: dict[str, dict] = {}
    for task in tasks:
        group = pairs.loc[pairs.task.eq(task)].copy()
        finite = group.precision_cosine[np.isfinite(group.precision_cosine)].to_numpy(float)
        if len(finite) == 0:
            raise SystemExit(f"no estimable deviation directions for {task}")
        observed = float(np.median(finite))
        boot = participant_bootstrap(finite, iterations=int(config["participant_bootstrap_iterations"]),
                                     seed=int(config["seed"]))
        null = permutation_null(endpoint, model, task=task, iterations=int(config["direction_permutations"]),
                                seed=int(config["seed"]))
        p = plus_one_p_value(observed, null)
        raw_p[task] = p
        records.append({
            "task": task,
            "n_paired": int(len(group)),
            "n_direction_estimable": int(len(finite)),
            "n_direction_excluded": int(len(group) - len(finite)),
            "median_precision_cosine": observed,
            "participant_bootstrap_ci_low": float(np.quantile(boot, 0.025)),
            "participant_bootstrap_ci_high": float(np.quantile(boot, 0.975)),
            "permutation_p_raw": p,
            "estimand": "six_plus_month_within_person_deviation_pattern_conservation",
        })
        null_rows.extend({"task": task, "draw": index + 1, "median_precision_cosine": value}
                         for index, value in enumerate(null))
        direction_summary[task] = {
            "n": int(len(group)),
            "median_precision_cosine": observed,
            "bootstrap_ci": [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))],
        }
    adjusted = holm_adjust(raw_p)
    for row in records:
        row["permutation_p_holm"] = adjusted[row["task"]]
        direction_summary[row["task"]]["holm_p"] = adjusted[row["task"]]
    args.output.mkdir(parents=True, exist_ok=True)
    # Participant identifiers remain local and must not be committed.
    pairs.to_csv(args.output / "deviation_direction_pairs_local.csv", index=False)
    pd.DataFrame(records).to_csv(args.output / "deviation_direction_summary.csv", index=False)
    pd.DataFrame(null_rows).to_csv(args.output / "deviation_direction_null.csv", index=False)
    _update_summary(args.output / "v4_6_summary.json", direction_summary)


if __name__ == "__main__":
    main()
