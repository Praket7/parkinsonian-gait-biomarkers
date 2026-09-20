import numpy as np


def quality_check(values, minimum_steps=3, max_missing_fraction=0.20):
    """Return machine-readable QC flags for one walking bout."""
    values = {k: np.asarray(v, dtype=float) for k, v in values.items() if v is not None}
    lengths = [len(v) for v in values.values()]
    n = max(lengths, default=0)
    missing = float(np.mean([np.isnan(v).mean() if len(v) else 1.0 for v in values.values()])) if values else 1.0
    reasons = []
    if n < minimum_steps:
        reasons.append("too_few_samples")
    if missing > max_missing_fraction:
        reasons.append("missing_fraction")
    if any(np.isinf(v).any() for v in values.values()):
        reasons.append("infinite_value")
    return {
        "n_samples": n,
        "missing_fraction": missing,
        "valid": not reasons,
        "reason_invalid": ";".join(reasons),
    }
