"""Prespecified multi-pass reliability helpers for the v4.4 extension."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.v4_3.walkway_reconstruction import FEATURES


def median_pass_endpoint(passes: pd.DataFrame, required_passes: int) -> pd.Series:
    """Return the declared median-input endpoint only for complete sessions."""
    if len(passes) != required_passes:
        raise ValueError(f"requires exactly {required_passes} valid passes, found {len(passes)}")
    return passes.loc[:, FEATURES].median(axis=0)


def variance_components(passes: pd.DataFrame) -> dict[str, float]:
    """Balanced nested ANOVA components: person, session-within-person, pass.

    The score is already computed per pass.  The result estimates reliability
    of a future *single session* formed from the declared number of passes.
    """
    cells = passes.pivot_table(index="participant", columns=["session", "pass"], values="score", aggfunc="first")
    if cells.empty or cells.isna().any().any():
        raise ValueError("complete balanced participant/session/pass data required")
    n_people = len(cells)
    sessions = passes.session.nunique()
    passes_per_session = passes.groupby(["participant", "session"]).size().unique()
    if len(passes_per_session) != 1 or n_people < 2 or sessions < 2:
        raise ValueError("balanced two-session repeated-pass data required")
    n_passes = int(passes_per_session[0])
    values = cells.to_numpy(float).reshape(n_people, sessions, n_passes)
    grand = values.mean()
    person_mean = values.mean(axis=(1, 2))
    session_mean = values.mean(axis=2)
    ms_person = sessions * n_passes * np.square(person_mean - grand).sum() / (n_people - 1)
    ms_session = n_passes * np.square(session_mean - person_mean[:, None]).sum() / (n_people * (sessions - 1))
    ms_pass = np.square(values - session_mean[:, :, None]).sum() / (n_people * sessions * (n_passes - 1))
    person = max((ms_person - ms_session) / (sessions * n_passes), 0.0)
    session = max((ms_session - ms_pass) / n_passes, 0.0)
    residual = max(ms_pass, 0.0)
    sem = float(np.sqrt(session + residual / n_passes))
    total = person + session + residual / n_passes
    return {
        "person_variance": float(person), "session_variance": float(session), "pass_variance": float(residual),
        "generalizability_coefficient": float(person / total) if total else float("nan"),
        "sem": sem, "mdc95": float(1.96 * np.sqrt(2) * sem), "n_passes": n_passes,
    }
