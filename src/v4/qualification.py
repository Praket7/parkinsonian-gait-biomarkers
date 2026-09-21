"""Context-of-use classification; execution status never implies evidence."""
from __future__ import annotations
import numpy as np


def classify(row, *, alpha=.05, icc_threshold=.60):
    if str(row.get("estimability_status", "OK")) != "OK": return "INSUFFICIENT_EVIDENCE"
    if row.get("measurement_error") == "FAIL": return "MEASUREMENT_LIMITED"
    if row.get("speed_construct") == "speed_is_part_of_construct": return "CHALLENGE_RESPONSE_CANDIDATE" if row.get("association_status") == "PASS" else "CONTEXT_SENSITIVE"
    if row.get("association_status") != "PASS": return "CONTEXT_SENSITIVE"
    if row.get("repeatability_icc", np.nan) < icc_threshold: return "MEASUREMENT_LIMITED"
    if row.get("task_transport") == "PASS" and row.get("site_transport") == "PASS": return "TRAIT_CANDIDATE"
    return "CONTEXT_SENSITIVE"


def evidence_row(feature, association, *, family, speed_construct, reliability=np.nan, task="NOT_ESTIMABLE", site="NOT_ESTIMABLE"):
    estimable = str(association.get("status", "NOT_ESTIMABLE")) == "OK"
    passed = bool(estimable and association.get("q_value", 1) <= .05)
    row = {"feature": feature, "family": family, "estimability_status": "OK" if estimable else "NOT_ESTIMABLE",
           "association_status": "PASS" if passed else "FAIL" if estimable else "INCOMPLETE",
           "repeatability_icc": reliability, "task_transport": task, "site_transport": site,
           "speed_construct": speed_construct, "measurement_error": "PASS"}
    row["classification"] = classify(row)
    return row
