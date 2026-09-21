"""Outcome-blind-free longitudinal stability summaries for a declared DMO family."""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def stability_selection(table, features, *, anchor="mdsscore3", iterations=100, seed=0):
    rng, rows = np.random.default_rng(seed), []
    for feature in features:
        frame = table[["participant_key", anchor, feature]].dropna() if feature in table else pd.DataFrame()
        people = frame.participant_key.unique() if not frame.empty else []
        effects = []
        for _ in range(iterations):
            chosen = rng.choice(people, max(1, len(people)//2), replace=False) if len(people) else []
            sample = frame[frame.participant_key.isin(chosen)]
            if sample.participant_key.nunique() >= 8 and sample[feature].nunique() >= 3:
                effects.append(spearmanr(sample[feature], sample[anchor]).statistic)
        values = np.asarray(effects, float)
        rows.append({"feature": feature, "n_participants": int(len(people)), "selection_probability": float(np.mean(abs(values) > .1)) if len(values) else np.nan,
                     "sign_consistency": float(max(np.mean(values >= 0), np.mean(values <= 0))) if len(values) else np.nan,
                     "median_standardized_effect": float(np.median(values)) if len(values) else np.nan,
                     "status": "OK" if len(values) == iterations else "NOT_ESTIMABLE"})
    return pd.DataFrame(rows)
