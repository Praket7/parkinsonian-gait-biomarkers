"""Small, deterministic validation helpers; scripts retain all clinical inference."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.model_selection import GroupKFold


def grouped_folds(table: pd.DataFrame, groups: str, n_splits=5):
    values = table[groups].astype(str).to_numpy()
    for train, test in GroupKFold(n_splits=min(n_splits, len(np.unique(values)))).split(table, groups=values):
        yield train, test


def metrics(actual, predicted) -> dict:
    actual, predicted = np.asarray(actual, float), np.asarray(predicted, float)
    slope, intercept = np.polyfit(predicted, actual, 1) if np.std(predicted) else (np.nan, np.nan)
    return {"mae": float(np.mean(np.abs(actual-predicted))), "rmse": float(np.sqrt(np.mean((actual-predicted)**2))),
            "spearman_rho": float(spearmanr(actual, predicted).statistic), "pearson_r": float(pearsonr(actual, predicted).statistic),
            "calibration_slope": float(slope), "calibration_intercept": float(intercept)}


def bootstrap_group_deltas(table: pd.DataFrame, model1: str, model2: str, iterations: int, seed: int) -> pd.DataFrame:
    rng, groups, rows = np.random.default_rng(seed), table.participant_id.astype(str).unique(), []
    for index in range(iterations):
        picked = rng.choice(groups, len(groups), replace=True)
        sample = pd.concat([table[table.participant_id.astype(str).eq(item)] for item in picked], ignore_index=True)
        a, b = metrics(sample.severity, sample[model1]), metrics(sample.severity, sample[model2])
        rows.append({"resample": index + 1, "delta_mae": b["mae"]-a["mae"], "delta_rmse": b["rmse"]-a["rmse"], "delta_rho": b["spearman_rho"]-a["spearman_rho"]})
    return pd.DataFrame(rows)
