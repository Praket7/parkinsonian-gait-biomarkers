"""Outcome-blind harmonic/regularity features for adequately long trunk traces."""
from __future__ import annotations
import numpy as np


def harmonic_ratio(signal, *, axis="ap", harmonics=10):
    signal = np.asarray(signal, float)
    if len(signal) < 2 * harmonics + 1 or not np.isfinite(signal).all(): return np.nan
    power = abs(np.fft.rfft(signal - signal.mean()))[1:harmonics+1]
    odd, even = power[::2].sum(), power[1::2].sum()
    return float((odd / even) if axis.lower() == "ml" and even else (even / odd) if odd else np.nan)


def stride_regularity(signal, lag):
    signal = np.asarray(signal, float)
    if lag < 1 or len(signal) <= lag or not np.isfinite(signal).all(): return np.nan
    return float(np.corrcoef(signal[:-lag], signal[lag:])[0, 1])
