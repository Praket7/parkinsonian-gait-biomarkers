#!/usr/bin/env python3
"""Render the six submission figures from committed aggregate outputs only."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def rows(root: Path, path: str) -> list[dict[str, str]]:
    with (root / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def finish(fig: plt.Figure, output: Path) -> None:
    fig.savefig(output, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def generate(root: Path) -> None:
    values = json.loads((root / "report/AAN_submission_values.json").read_text(encoding="utf-8"))
    target = root / "report/figures/final"
    target.mkdir(parents=True, exist_ok=True)
    navy, blue, teal, amber, gray = "#20344A", "#3478A8", "#3E887B", "#D49A45", "#687785"
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.titleweight": "bold"})

    stages = [
        "Healthy-control reference\n(no PD outcomes used)", "Frozen eight-input\n deviation score",
        "Severity association", "2,000 reference\nresamples", "External transport\nboundary",
        "Six-plus-month\nstability", "252-trial analytical\nbridge", "Grouped validation\nbeyond speed",
    ]
    fig, ax = plt.subplots(figsize=(12, 5.2))
    ax.axis("off")
    x = np.linspace(.14, .86, 4)
    top_y, bottom_y = .68, .32
    for i, label in enumerate(stages):
        row, col = divmod(i, 4)
        cx, cy = (x[col], top_y if row == 0 else bottom_y)
        color = amber if i == 4 else teal
        ax.text(cx, cy, label, ha="center", va="center", color=navy, fontsize=9,
                bbox={"boxstyle": "round,pad=.72", "facecolor": "#F3F6F7", "edgecolor": color, "linewidth": 2},
                transform=ax.transAxes)
    for i in range(3):
        ax.annotate("", xy=(x[i + 1] - .07, top_y), xytext=(x[i] + .07, top_y),
                    xycoords=ax.transAxes, arrowprops={"arrowstyle": "->", "color": gray, "lw": 1.6})
        ax.annotate("", xy=(x[i] + .07, bottom_y), xytext=(x[i + 1] - .07, bottom_y),
                    xycoords=ax.transAxes, arrowprops={"arrowstyle": "->", "color": gray, "lw": 1.6})
    ax.annotate("", xy=(x[-1], bottom_y + .085), xytext=(x[-1], top_y - .085),
                xycoords=ax.transAxes, arrowprops={"arrowstyle": "->", "color": gray, "lw": 1.6})
    ax.text(.5, .91, "Validation sequence: each question is a separate evidence layer",
            ha="center", color=navy, fontsize=16, weight="bold", transform=ax.transAxes)
    ax.text(.5, .08, "Blue-green: supported evidence   •   Amber: a boundary or unresolved validation question",
            ha="center", color=gray, fontsize=9, transform=ax.transAxes)
    finish(fig, target / "figure_1_study_design.png")

    primary = rows(root, values["source_files"]["primary"])
    effect = next(r for r in primary if r["feature"] == "context_adjusted_gait_deviation_v1")
    boot = rows(root, values["source_files"]["reference_bootstrap"])
    effects = np.array([float(r["effect"]) for r in boot])
    fig, (left, right) = plt.subplots(1, 2, figsize=(11, 4.5), gridspec_kw={"width_ratios": [1, 1.5]})
    left.errorbar([float(effect["effect"])], [0],
                  xerr=[[float(effect["effect"]) - float(effect["ci_low"])],
                        [float(effect["ci_high"]) - float(effect["effect"])]],
                  fmt="o", color=blue, capsize=5, markersize=8)
    left.axvline(0, color=gray, lw=1, ls="--")
    left.set(yticks=[0], yticklabels=["Primary score"], xlabel="Standardized severity association",
             title="Primary estimate")
    left.text(.04, .93, f"β = {float(effect['effect']):.3f}\n95% CI {float(effect['ci_low']):.3f} to {float(effect['ci_high']):.3f}\nq = {float(effect['q_value']):.4f}",
              transform=left.transAxes, va="top", color=navy)
    right.hist(effects, bins=28, color=blue, alpha=.78, edgecolor="white")
    right.axvline(0, color=gray, ls="--", lw=1.5, label="No association")
    right.axvline(np.median(effects), color=teal, lw=2, label=f"Median {np.median(effects):.3f}")
    right.set(xlabel="Effect after healthy-reference resampling", ylabel="Resamples",
              title="Reference robustness (2,000 resamples)")
    right.legend(frameon=False)
    fig.suptitle("Association and reference robustness are supported; they do not qualify stability", color=navy, weight="bold")
    fig.tight_layout()
    finish(fig, target / "figure_2_reference_robustness.png")

    repeated = rows(root, values["source_files"]["h2_repeated"])
    participant = [r for r in repeated if r["level"] == "participant"]
    rho = np.array([float(r["delta_spearman_rho"]) for r in participant])
    rmse = np.array([float(r["delta_rmse"]) for r in participant])
    summary = rows(root, values["source_files"]["h2_summary"])
    psummary = next(r for r in summary if r["level"] == "participant")
    corrected = rows(root, values["source_files"]["h2_corrected"])
    pcorrected = next(r for r in corrected if r["level"] == "participant")
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))
    axes[0].hist(rho, bins=18, color=teal, edgecolor="white")
    axes[0].axvline(0, color=gray, ls="--")
    axes[0].axvline(np.median(rho), color=navy, lw=2)
    axes[0].set(title="Severity ranking", xlabel="Extended minus baseline Spearman ρ", ylabel="Repeated splits")
    axes[0].text(.04, .94, f"Median Δρ = {np.median(rho):.3f}\nImproved in {float(psummary['delta_spearman_rho_favorable_fraction']):.0%}",
                 transform=axes[0].transAxes, va="top", color=navy)
    axes[1].hist(rmse, bins=18, color=amber, edgecolor="white")
    axes[1].axvline(0, color=gray, ls="--")
    axes[1].axvline(np.median(rmse), color=navy, lw=2)
    axes[1].set(title="Absolute error", xlabel="Extended minus baseline RMSE", ylabel="Repeated splits")
    axes[1].text(.04, .94, f"Median ΔRMSE = {np.median(rmse):.3f}\nLower in {float(psummary['delta_rmse_favorable_fraction']):.0%}",
                 transform=axes[1].transAxes, va="top", color=navy)
    metrics = ["Rank (ρ)", "Pearson r", "Lower RMSE", "Lower MAE", "Slope closer to 1", "Intercept closer to 0"]
    fractions = [float(psummary["delta_spearman_rho_favorable_fraction"]),
                 float(psummary["delta_pearson_r_favorable_fraction"]),
                 float(psummary["delta_rmse_favorable_fraction"]),
                 float(psummary["delta_mae_favorable_fraction"]),
                 float(pcorrected["delta_calibration_slope_favorable_fraction"]),
                 float(pcorrected["delta_calibration_intercept_favorable_fraction"])]
    bars = axes[2].barh(metrics, fractions, color=[teal, blue, amber, amber, amber, amber])
    axes[2].axvline(.5, color=gray, ls="--")
    axes[2].set(xlim=(0, 1), xlabel="Participant-level repeats favoring score", title="How often did it help?")
    for bar, val in zip(bars, fractions):
        axes[2].text(min(val + .02, .96), bar.get_y() + bar.get_height()/2, f"{val:.0%}",
                     va="center", ha="left" if val < .9 else "right", color=navy, fontsize=8)
    fig.suptitle("The score improves ordering more consistently than exact prediction", color=navy, weight="bold")
    fig.tight_layout()
    finish(fig, target / "figure_3_incremental_validation.png")

    bridge = rows(root, values["source_files"]["bridge"])
    labels = [r["feature"].replace("_mean", "").replace("_", " ") for r in bridge]
    icc = np.array([float(r["icc_a1"]) for r in bridge])
    ccc = np.array([float(r["ccc"]) for r in bridge])
    thresholds = np.array([.85 if "cv" in r["feature"] else .90 for r in bridge])
    bias = np.array([100 * float(r["relative_bias"]) for r in bridge])
    fig, (left, right) = plt.subplots(1, 2, figsize=(12, 5.3), gridspec_kw={"width_ratios": [1.8, 1]})
    y = np.arange(len(labels))
    for i, threshold in enumerate(thresholds):
        left.plot([threshold, 1.005], [y[i], y[i]], color="#DCE6E8", lw=5, zorder=0)
    left.scatter(icc, y - .09, label="ICC(A,1)", color=blue, s=46, zorder=2)
    left.scatter(ccc, y + .09, label="CCC", color=teal, s=46, marker="s", zorder=2)
    for i, threshold in enumerate(thresholds):
        left.plot([threshold, threshold], [y[i] - .34, y[i] + .34], color=amber, lw=1.4)
    left.set(yticks=y, yticklabels=labels, xlim=(.82, 1.01), xlabel="Agreement statistic",
             title="All eight inputs passed their frozen gate")
    left.invert_yaxis()
    left.legend(frameon=False, loc="lower right")
    right.barh(y, bias, color=blue, alpha=.8)
    right.axvline(0, color=gray, lw=1)
    right.set(yticks=y, yticklabels=[], xlabel="Relative bias (%)", title="Reconstruction bias")
    right.invert_yaxis()
    fig.suptitle("Raw walkway reconstruction against PKMAS: 252 matched trials", color=navy, weight="bold")
    fig.text(.49, .01, "Amber markers show the frozen threshold: 0.90 for means and 0.85 for variability measures. No confidence intervals were stored for this bridge.",
             ha="center", color=gray, fontsize=8)
    fig.tight_layout(rect=(0, .05, 1, .94))
    finish(fig, target / "figure_4_measurement_validation.png")

    point = rows(root, values["source_files"]["longitudinal_point"])
    intervals = rows(root, values["source_files"]["longitudinal_ci"])
    selected = [("SelfPace", "Self-paced"), ("HurriedPace", "Hurried pace")]
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    for y, (task, label) in enumerate(selected):
        p = next(r for r in point if r["task"] == task)
        ci = next(r for r in intervals if r["task"] == task)
        xval, lo, hi = float(p["icc_a1"]), float(ci["icc_bca_ci_low"]), float(ci["icc_bca_ci_high"])
        ax.errorbar(xval, y, xerr=[[xval-lo], [hi-xval]], fmt="o", color=blue, capsize=6, markersize=8)
        ax.text(.98, y + (.18 if y == 0 else -.18),
                f"n={p['n_participants']}   ICC={xval:.3f}   95% BCa CI {lo:.3f} to {hi:.3f}",
                transform=ax.get_yaxis_transform(), ha="right", va="center", color=navy, fontsize=8.5)
    ax.axvline(.8, color=amber, ls="--", label="Prespecified lower-bound criterion = 0.80")
    ax.axvline(0, color=gray, lw=1)
    ax.set(yticks=[0, 1], yticklabels=[x[1] for x in selected], xlim=(-.12, 1.68),
           xlabel="Six-plus-month longitudinal ICC(A,1)",
           title="Six-plus-month stability did not meet the lower-bound criterion (0.80)")
    ax.invert_yaxis()
    fig.text(.5, .02, "These visits do not estimate short-term, state-controlled test–retest reliability.", ha="center", color=gray, fontsize=9)
    fig.tight_layout(rect=(0, .07, 1, 1))
    finish(fig, target / "figure_5_longitudinal_stability.png")

    evidence = [
        ("Severity association", "SUPPORTED", teal),
        ("Healthy-reference robustness", "SUPPORTED", teal),
        ("Incremental severity ranking", "SUPPORTED", teal),
        ("Exact-score prediction advantage", "INCOMPLETE", amber),
        ("Eight-input analytical reconstruction", "SUPPORTED", teal),
        ("Six-plus-month stability", "FAILED", "#B7684C"),
        ("Short-term reliability", "NOT ESTIMABLE", gray),
        ("Clinical responsiveness", "NOT ESTIMABLE", gray),
        ("CARE-PD frozen-score transport", "NOT ESTIMABLE", gray),
        ("Medication response", "NOT ESTIMABLE", gray),
        ("Broad multisite transport", "NOT ESTIMABLE", gray),
    ]
    fig, ax = plt.subplots(figsize=(9, 6.5))
    ax.axis("off")
    ax.text(.05, .95, "Evidence is layered; an unresolved or failed layer does not erase a supported one",
            transform=ax.transAxes, ha="left", va="top", color=navy, fontsize=14, weight="bold")
    for i, (claim, status, color) in enumerate(evidence):
        yy = .84 - i * .073
        ax.text(.05, yy, claim, transform=ax.transAxes, va="center", color=navy, fontsize=10)
        ax.text(.96, yy, status, transform=ax.transAxes, va="center", ha="right", color=color,
                fontsize=9, weight="bold", bbox={"boxstyle": "round,pad=.35", "facecolor": "white", "edgecolor": color})
        if i < len(evidence)-1:
            ax.plot([.05, .96], [yy-.042, yy-.042], transform=ax.transAxes, color="#E4E9EC", lw=.7)
    finish(fig, target / "figure_6_evidence_ladder.png")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    generate(args.root.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
