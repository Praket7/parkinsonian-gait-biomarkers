"""The small, data-backed analysis path used for the authorized releases.

The reference-walkway table is the primary V1 measurement.  Contact-derived
metrics are deliberately a validation/reliability layer, never a substitute
for unvalidated spatial or pressure-walkway variables.
"""
from __future__ import annotations

import json
from pathlib import Path
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import spearmanr

from .carepd_speed import speed_from_pickle
from .io import infer_task
from .stats import bh_fdr
from .walkway import load_walkway_metrics
from .weargait import read_weargait_csv
from .weargait_clinical import join_clinical_features, load_v1_clinical


PRIMARY_FEATURES = [
    "gait_speed", "cadence", "step_length_mean", "stride_length_mean",
    "step_time_mean", "stride_time_mean", "step_time_cv", "stride_time_cv",
    "stance_fraction", "swing_fraction", "double_support_fraction",
]
CONTACT_FEATURES = ["cadence", "step_time_mean", "step_time_cv", "stride_time_mean", "stride_time_cv"]
PRIMARY_TASKS = {"SP", "HP"}
RAW_CONTEXT_TASKS = {"SP", "HP", "SPm", "HPm"}


def _z(values: pd.Series) -> pd.Series:
    values = pd.to_numeric(values, errors="coerce")
    sd = values.std(ddof=0)
    return (values - values.mean()) / sd if np.isfinite(sd) and sd else values * np.nan


def _selected_contacts(root: Path, tasks: set[str]) -> pd.DataFrame:
    """Read only the requested signals; filenames are filtered before CSV IO."""
    rows = []
    for path in sorted(root.rglob("*.csv")):
        if infer_task(path) in tasks:
            try:
                rows.append(read_weargait_csv(path))
            except ValueError:
                pass
    return pd.DataFrame(rows)


def _gee_associations(table: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    """One participant-clustered, context-adjusted standardized association/model."""
    rows = []
    for feature in features:
        keep = [feature, "mds_updrs_gait_item", "age", "height_m", "sex", "task", "site", "participant_id"]
        frame = table[keep].dropna().copy()
        if len(frame) < 30 or frame.participant_id.nunique() < 20 or frame[feature].nunique() < 4:
            rows.append({"feature": feature, "n_rows": len(frame), "n_participants": frame.participant_id.nunique(), "effect": np.nan, "ci_low": np.nan, "ci_high": np.nan, "p_value": np.nan})
            continue
        frame["outcome_z"] = _z(frame[feature])
        frame["severity_z"] = _z(frame["mds_updrs_gait_item"])
        frame["age_z"] = _z(frame.age)
        frame["height_z"] = _z(frame.height_m)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = sm.GEE.from_formula(
                    "outcome_z ~ severity_z + age_z + height_z + C(sex) + C(task) + C(site)",
                    groups="participant_id", data=frame, cov_struct=sm.cov_struct.Exchangeable(), family=sm.families.Gaussian(),
                ).fit()
            term = "severity_z"
            rows.append({"feature": feature, "n_rows": len(frame), "n_participants": frame.participant_id.nunique(),
                         "effect": float(model.params[term]), "ci_low": float(model.conf_int().loc[term, 0]),
                         "ci_high": float(model.conf_int().loc[term, 1]), "p_value": float(model.pvalues[term])})
        except (ValueError, np.linalg.LinAlgError):
            rows.append({"feature": feature, "n_rows": len(frame), "n_participants": frame.participant_id.nunique(), "effect": np.nan, "ci_low": np.nan, "ci_high": np.nan, "p_value": np.nan})
    result = pd.DataFrame(rows)
    result["q_value"] = bh_fdr(result.p_value)
    return result


def _bootstrap_direction(table: pd.DataFrame, features: list[str], iterations: int, seed: int) -> pd.Series:
    """Cluster bootstrap point-estimate direction (the GEE remains primary).

    A bootstrap needs coefficients, not 2,000 repeated robust-covariance fits.
    The fixed design is therefore built once and participants, with all their
    task rows, are resampled by index.
    """
    people, rng, output = table.participant_id.dropna().unique(), np.random.default_rng(seed), {}
    for feature in features:
        keep = [feature, "mds_updrs_gait_item", "age", "height_m", "sex", "task", "site", "participant_id"]
        frame = table[keep].dropna().copy()
        frame["severity_z"] = _z(frame.mds_updrs_gait_item); frame["age_z"] = _z(frame.age); frame["height_z"] = _z(frame.height_m); frame["outcome_z"] = _z(frame[feature])
        design = pd.get_dummies(frame[["severity_z", "age_z", "height_z", "sex", "task", "site"]], columns=["sex", "task", "site"], drop_first=True, dtype=float)
        x, y = np.c_[np.ones(len(design)), design.to_numpy(float)], frame.outcome_z.to_numpy(float)
        groups = {person: np.flatnonzero(frame.participant_id.eq(person)) for person in frame.participant_id.unique()}
        eligible = np.array(list(groups))
        if len(eligible) < 20:
            output[feature] = np.nan; continue
        signs = []
        for _ in range(iterations):
            index = np.concatenate([groups[p] for p in rng.choice(eligible, size=len(eligible), replace=True)])
            value = np.linalg.lstsq(x[index], y[index], rcond=None)[0][1]
            signs.append(np.sign(value))
        output[feature] = float(abs(np.mean(signs)))
    return pd.Series(output, name="direction_consistency")


def _variance_components(table: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    """Mixed-model participant/residual components, plus fixed context spread."""
    rows = []
    for feature in features:
        frame = table[[feature, "participant_id", "task", "site"]].dropna().copy()
        if len(frame) < 30 or frame.participant_id.nunique() < 20:
            continue
        frame["outcome_z"] = _z(frame[feature])
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                fit = sm.MixedLM.from_formula("outcome_z ~ C(task) + C(site)", groups="participant_id", data=frame).fit(reml=True, method="lbfgs", disp=False)
            fixed = fit.model.exog[:, 1:] @ fit.fe_params.to_numpy()[1:]
            participant_var, residual_var = float(fit.cov_re.iloc[0, 0]), float(fit.scale)
            total = participant_var + residual_var + float(np.var(fixed, ddof=1))
            rows.append({"feature": feature, "n_rows": len(frame), "participant_fraction": participant_var / total,
                         "context_fixed_fraction": float(np.var(fixed, ddof=1)) / total, "residual_fraction": residual_var / total,
                         "participant_variance": participant_var, "residual_variance": residual_var})
        except (ValueError, np.linalg.LinAlgError):
            rows.append({"feature": feature, "n_rows": len(frame), "participant_fraction": np.nan, "context_fixed_fraction": np.nan, "residual_fraction": np.nan, "participant_variance": np.nan, "residual_variance": np.nan})
    return pd.DataFrame(rows)


def _validation(reference: pd.DataFrame, contacts: pd.DataFrame) -> pd.DataFrame:
    merged = contacts.merge(reference[["participant_id", "task", "cadence", "step_time_mean"]], on=["participant_id", "task"], suffixes=("_contact", "_walkway"), validate="many_to_one")
    rows = []
    for metric in ("cadence", "step_time_mean"):
        frame = merged[[f"{metric}_contact", f"{metric}_walkway"]].dropna()
        difference = frame.iloc[:, 0] - frame.iloc[:, 1]
        rows.append({"metric": metric, "n": len(frame), "spearman_rho": spearmanr(frame.iloc[:, 0], frame.iloc[:, 1]).statistic if len(frame) > 2 else np.nan,
                     "mean_bias": difference.mean(), "mae": difference.abs().mean(), "rmse": np.sqrt(np.mean(difference**2))})
    return pd.DataFrame(rows), merged


def _icc(table: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    rows = []
    for feature in features:
        frame = table[["participant_id", "session_id", "task", feature]].dropna()
        wide = frame.pivot_table(index=["participant_id", "task"], columns="session_id", values=feature, aggfunc="mean").dropna()
        if wide.shape[0] < 5 or wide.shape[1] < 2:
            rows.append({"feature": feature, "n_pairs": len(wide), "icc_2_1": np.nan, "sem": np.nan, "mdc95": np.nan}); continue
        values = wide.iloc[:, :2].to_numpy(float)
        n = len(values)
        ms_subject = 2 * np.var(values.mean(axis=1), ddof=1)
        ms_error = np.sum((values - values.mean(axis=1, keepdims=True)) ** 2) / n
        icc = (ms_subject - ms_error) / (ms_subject + ms_error)
        sem = np.sqrt(ms_error)
        rows.append({"feature": feature, "n_pairs": n, "icc_2_1": icc, "sem": sem, "mdc95": 1.96 * np.sqrt(2) * sem})
    return pd.DataFrame(rows)


def _care_replication(care_root: Path, outdir: Path) -> tuple[pd.DataFrame, dict]:
    canonical = care_root / "Canonicalized_SMPL_pickles"
    paths = [canonical / f"{name}_canonical.pkl" for name in ("3DGait", "BMCLab", "PD-GaM", "T-SDU-PD")]
    frames = [speed_from_pickle(path) for path in paths if path.exists()]
    if not frames:
        return pd.DataFrame(), {"status": "not_available"}
    table = pd.concat(frames, ignore_index=True)
    table["mds_updrs_gait_item"] = pd.to_numeric(table.mds_updrs_gait_item, errors="coerce")
    # Canonical CARE coordinates define z as forward.  Keep only clearly
    # forward, plausible walks: this is a prespecified QC guard, not tuning.
    clean = table[(table.speed_axis.eq(2)) & table.global_forward_speed_m_s.between(0.2, 3.0) & table.mds_updrs_gait_item.notna()].copy()
    clean["speed_z"] = _z(clean.global_forward_speed_m_s)
    clean["severity_z"] = _z(clean.mds_updrs_gait_item)
    # Participant IDs are cohort-local (several cohorts number from zero), so
    # they must never be clustered as though they identify one person globally.
    clean["care_participant_key"] = clean.cohort.astype(str) + ":" + clean.participant_id.astype(str)
    if clean.care_participant_key.nunique() >= 20 and clean.mds_updrs_gait_item.nunique() >= 3:
        model = sm.GEE.from_formula("speed_z ~ severity_z + C(cohort)", groups="care_participant_key", data=clean, family=sm.families.Gaussian()).fit()
        effect = float(model.params.severity_z)
        interval = model.conf_int().loc["severity_z"]
        result = {"status": "translation_speed_only", "n_trials": int(len(clean)), "n_participants": int(clean.care_participant_key.nunique()), "effect": effect, "ci_low": float(interval.iloc[0]), "ci_high": float(interval.iloc[1]), "p_value": float(model.pvalues.severity_z)}
    else:
        result = {"status": "insufficient_after_forward_trajectory_qc", "n_trials": int(len(clean)), "n_participants": int(clean.care_participant_key.nunique())}
    table.to_csv(outdir / "carepd_translation_speed_all_trials.csv", index=False)
    clean.to_csv(outdir / "carepd_translation_speed_qc.csv", index=False)
    return clean, result


def _figures(outdir: Path, associations: pd.DataFrame, variance: pd.DataFrame, validation: pd.DataFrame, reliability: pd.DataFrame, care: dict) -> None:
    figures = outdir / "figures"; figures.mkdir(exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(7, 4)); plot = associations.dropna(subset=["effect"]).sort_values("effect")
    ax.errorbar(plot.effect, range(len(plot)), xerr=[plot.effect - plot.ci_low, plot.ci_high - plot.effect], fmt="o", color="#126782")
    ax.axvline(0, color="black", lw=1); ax.set_yticks(range(len(plot)), plot.feature); ax.set_xlabel("Standardized association with MDS-UPDRS III gait item"); fig.tight_layout(); fig.savefig(figures / "figure_1_primary_forest.png", dpi=220); plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 4)); plot = variance.dropna(subset=["participant_fraction"])
    ax.bar(plot.feature, plot.participant_fraction, label="participant"); ax.bar(plot.feature, plot.context_fixed_fraction, bottom=plot.participant_fraction, label="task/site"); ax.bar(plot.feature, plot.residual_fraction, bottom=plot.participant_fraction + plot.context_fixed_fraction, label="residual")
    ax.set_ylim(0, 1); ax.tick_params(axis="x", rotation=60); ax.legend(); fig.tight_layout(); fig.savefig(figures / "figure_2_variance.png", dpi=220); plt.close(fig)
    fig, ax = plt.subplots(figsize=(6, 3.5)); ax.bar(validation.metric, validation.spearman_rho, color="#6a3d9a"); ax.set_ylim(-1, 1); ax.set_ylabel("Spearman agreement with walkway"); fig.tight_layout(); fig.savefig(figures / "figure_3_contact_validation.png", dpi=220); plt.close(fig)
    fig, ax = plt.subplots(figsize=(6, 3.5)); ax.bar(reliability.feature, reliability.icc_2_1, color="#1b9e77"); ax.axhline(.6, ls="--", color="black"); ax.set_ylim(-1, 1); ax.tick_params(axis="x", rotation=45); ax.set_ylabel("Session ICC(2,1)"); fig.tight_layout(); fig.savefig(figures / "figure_4_longitudinal_reliability.png", dpi=220); plt.close(fig)
    fig, ax = plt.subplots(figsize=(5, 3.5)); effect = care.get("effect", np.nan); ax.bar(["CARE translation\nspeed"], [effect], color="#d95f02"); ax.errorbar([0], [effect], yerr=[[effect-care.get("ci_low", effect)], [care.get("ci_high", effect)-effect]], fmt="none", color="black"); ax.axhline(0, color="black", lw=1); ax.set_ylabel("Standardized severity association"); fig.tight_layout(); fig.savefig(figures / "figure_5_carepd_translation_check.png", dpi=220); plt.close(fig)


def run_authorized_analysis(data_root, output_dir, *, seed=20260920, bootstrap_iterations=200) -> dict:
    """Run all analysis steps that are supported by locally authorized files."""
    root, outdir = Path(data_root), Path(output_dir); outdir.mkdir(parents=True, exist_ok=True)
    v1 = root / "WearGait_PD_V1"; v2 = root / "WearGait_PD_Longitudinal"; care = root / "CARE_PD"
    walkway = load_walkway_metrics(v1 / "Walkway-derived metrics" / "PKMAS Walkway Gait Metrics - HP+SP.csv")
    clinical = load_v1_clinical(v1 / "PD - Demographic+Clinical - datasetV1.csv", v1 / "CONTROLS - Demographic+Clinical - datasetV1.csv")
    reference = join_clinical_features(walkway, clinical)
    reference.to_csv(outdir / "v1_reference_walkway_clinical.csv", index=False)
    pd_primary = reference[reference.clinical_cohort.eq("pd") & reference.task.isin(PRIMARY_TASKS) & reference.mds_updrs_gait_item.notna()].copy()
    associations = _gee_associations(pd_primary, PRIMARY_FEATURES)
    associations["direction_consistency"] = _bootstrap_direction(pd_primary, PRIMARY_FEATURES, bootstrap_iterations, seed).reindex(associations.feature).to_numpy()
    associations.to_csv(outdir / "primary_associations.csv", index=False)
    variance = _variance_components(pd_primary, PRIMARY_FEATURES); variance.to_csv(outdir / "variance_components.csv", index=False)
    v1_contacts = _selected_contacts(v1, RAW_CONTEXT_TASKS); v1_contacts = join_clinical_features(v1_contacts, clinical); v1_contacts.to_csv(outdir / "v1_contact_features.csv", index=False)
    validation, _ = _validation(walkway[walkway.task.isin(PRIMARY_TASKS)], v1_contacts[v1_contacts.task.isin(PRIMARY_TASKS)]); validation.to_csv(outdir / "contact_walkway_validation.csv", index=False)
    v2_contacts = _selected_contacts(v2, RAW_CONTEXT_TASKS); v2_contacts.to_csv(outdir / "v2_contact_features.csv", index=False)
    reliability = _icc(v2_contacts, CONTACT_FEATURES); reliability.to_csv(outdir / "longitudinal_reliability.csv", index=False)
    _, care_result = _care_replication(care, outdir)
    reliable = set(reliability.loc[reliability.icc_2_1.ge(.6), "feature"])
    valid = set(validation.loc[validation.spearman_rho.ge(.7), "metric"])
    associations["trait_eligible"] = associations.apply(lambda r: bool(r.q_value <= .05 and r.direction_consistency >= .8 and r.feature in reliable and r.feature in valid), axis=1)
    associations.to_csv(outdir / "primary_associations.csv", index=False)
    traits = associations.loc[associations.trait_eligible, "feature"].tolist()
    _figures(outdir, associations, variance, validation, reliability, care_result)
    manifest = {"analysis_version": "2.0", "seed": seed, "primary_data": "WearGait V1 PKMAS reference walkway", "n_reference_rows": int(len(reference)), "n_primary_rows": int(len(pd_primary)), "n_primary_participants": int(pd_primary.participant_id.nunique()), "primary_target": "MDS-UPDRS Part III item 3.10 (gait)", "trait_features": traits, "hypothesis": "not_supported_under_strict_criteria" if not traits else "supported_for_listed_candidates", "contact_validation": validation.to_dict(orient="records"), "longitudinal": reliability.to_dict(orient="records"), "carepd": care_result, "limits": ["V1 reference-walkway table contains SP/HP only.", "Longitudinal source has no linked repeated clinical-score table; change-versus-severity was not estimated.", "CARE-PD result is a canonical global-translation check, not a gait-event replication."], "status": "analysis_complete"}
    (outdir / "frozen").mkdir(exist_ok=True)
    (outdir / "frozen" / "results.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest
