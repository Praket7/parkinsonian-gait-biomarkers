#!/usr/bin/env python3
"""Render identifier-free v3 figures from frozen aggregate tables."""
from pathlib import Path
import argparse

import matplotlib.pyplot as plt
import pandas as pd


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve(); frozen = root / "results" / "frozen"
    output = root / "results" / "figures"; output.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")
    primary = pd.read_csv(frozen / "primary_associations.csv").sort_values("effect")
    fig, ax = plt.subplots(figsize=(8, 5)); y = range(len(primary))
    ax.errorbar(primary.effect, y, xerr=[primary.effect-primary.ci_low, primary.ci_high-primary.effect], fmt="o", color="#126782")
    ax.axvline(0, color="black", lw=1); ax.set_yticks(list(y), primary.feature); ax.set_xlabel("Primary standardized GEE severity association")
    fig.tight_layout(); fig.savefig(output / "figure_1_primary_forest.png", dpi=220); plt.close(fig)
    evidence = pd.read_csv(frozen / "feature_evidence_matrix.csv")
    fig, ax = plt.subplots(figsize=(8, 4)); plot = evidence.sort_values("bootstrap_same_sign_fraction")
    ax.bar(plot.feature, plot.bootstrap_same_sign_fraction, color="#6a3d9a"); ax.axhline(.8, ls="--", color="black", label="configured threshold")
    ax.set_ylim(0, 1.05); ax.tick_params(axis="x", rotation=55); ax.set_ylabel("GEE bootstrap same-sign fraction"); ax.legend(); fig.tight_layout(); fig.savefig(output / "figure_2_bootstrap_stability.png", dpi=220); plt.close(fig)
    reliability = pd.read_csv(frozen / "reliability.csv"); reliability["label"] = reliability.feature + " / " + reliability.task
    fig, ax = plt.subplots(figsize=(8, 4)); plot = reliability.sort_values("icc_2_1")
    ax.bar(plot.label, plot.icc_2_1, color="#1b9e77"); ax.axhline(.6, ls="--", color="black"); ax.set_ylim(-1, 1); ax.tick_params(axis="x", rotation=55); ax.set_ylabel("ICC(A,1)"); fig.tight_layout(); fig.savefig(output / "figure_3_task_reliability.png", dpi=220); plt.close(fig)
    validation = pd.read_csv(frozen / "contact_validation.csv")
    fig, ax = plt.subplots(figsize=(7, 4)); ax.bar(validation.feature, validation.spearman_rho, color="#d95f02"); ax.axhline(.7, ls="--", color="black"); ax.set_ylim(-1, 1); ax.tick_params(axis="x", rotation=45); ax.set_ylabel("Contact versus PKMAS Spearman rho"); fig.tight_layout(); fig.savefig(output / "figure_4_contact_validation.png", dpi=220); plt.close(fig)
    care = pd.read_csv(frozen / "carepd_cohort_results.csv"); plot = care[care.outcome.eq("endpoint_z_speed_m_s")]
    fig, ax = plt.subplots(figsize=(7, 4)); y = range(len(plot)); ax.errorbar(plot.effect, y, xerr=[plot.effect-plot.ci_low, plot.ci_high-plot.effect], fmt="o", color="#e7298a")
    ax.axvline(0, color="black", lw=1); ax.set_yticks(list(y), plot.cohort); ax.set_xlabel("Cohort-specific CARE translation-speed association"); fig.tight_layout(); fig.savefig(output / "figure_5_care_cohorts.png", dpi=220); plt.close(fig)
    # The release-facing synthesis: each symbol is a frozen evidence decision,
    # never a row-level observation or a manually typed result.
    columns = [
        ("Severity", "severity_status"), ("Speed", "speed_status"),
        ("Task", "task_robustness_status"), ("Site", "site_robustness_status"),
        ("Reliability", "reliability_status"), ("Analytical", "analytical_validation_status"),
        ("External", "external_replication_status"),
    ]
    symbols = {"PASS": "✓", "FAIL": "×", "NOT_ESTIMABLE": "?", "NOT_APPLICABLE": "—", "LIMITED_TRANSLATION_CHECK": "—"}
    fig, ax = plt.subplots(figsize=(10, 5.5)); ax.set_xlim(0, len(columns)); ax.set_ylim(0, len(evidence)); ax.invert_yaxis()
    for row_index, row in enumerate(evidence.itertuples(index=False)):
        for col_index, (_, key) in enumerate(columns):
            status = getattr(row, key, "NOT_ESTIMABLE")
            ax.text(col_index + .5, row_index + .5, symbols.get(status, "?"), ha="center", va="center", fontsize=16,
                    color={"PASS":"#13795b", "FAIL":"#b42318"}.get(status, "#555"))
    ax.set_xticks([i + .5 for i in range(len(columns))], [name for name, _ in columns]); ax.set_yticks([i + .5 for i in range(len(evidence))], evidence.feature)
    ax.set_title("Evidence matrix: ✓ pass, × fail, ? not estimable, — not applicable / limited check")
    ax.grid(True, color="#ddd"); fig.tight_layout(); fig.savefig(output / "figure_6_evidence_matrix.png", dpi=220); plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
