"""Outcome-blind contact-event quality control."""
from __future__ import annotations
import numpy as np


def clean_alternating_contacts(left, right, *, minimum=0.25, maximum=2.0):
    """Return ordered alternating contacts and their labels, or empty arrays."""
    left, right = np.asarray(left, float), np.asarray(right, float)
    left, right = left[np.isfinite(left)], right[np.isfinite(right)]
    times = np.r_[left, right]; labels = np.r_[np.zeros(len(left), int), np.ones(len(right), int)]
    order = np.argsort(times, kind="stable"); times, labels = times[order], labels[order]
    if len(times) < 2:
        return np.array([]), np.array([], dtype=int)
    keep = np.r_[True, (np.diff(times) >= minimum) & (np.diff(times) <= maximum) & (labels[1:] != labels[:-1])]
    return times[keep], labels[keep]


def event_qc(left, right, *, minimum_cycles=30, minimum=0.25, maximum=2.0, alternation_min=.80):
    times, labels = clean_alternating_contacts(left, right, minimum=minimum, maximum=maximum)
    alternation = float(np.mean(np.diff(labels) != 0)) if len(labels) > 1 else 0.0
    return {"times": times, "labels": labels, "n_events": int(len(times)), "n_cycles": int(len(times) // 2),
            "alternation_fraction": alternation, "status": "OK" if len(times) // 2 >= minimum_cycles and alternation >= alternation_min else "NOT_ESTIMABLE"}
