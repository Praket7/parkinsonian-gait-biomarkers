from __future__ import annotations

import json
from pathlib import Path

from scripts.build_v4_6_report import render_report
from scripts.check_v4_6_claims import find_unsupported_claims


def synthetic_summary() -> dict:
    return {
        "historical_score": {"status": "UNCHANGED", "longitudinal_interval": "six_plus_months"},
        "score_level_analytical_agreement": {"n": 252, "icc_a1": 0.99, "ccc": 0.99, "mae": 0.05, "rmse": 0.07},
        "longitudinal_direction_conservation": {
            "SelfPace": {"n": 45, "median_precision_cosine": 0.72, "bootstrap_ci": [0.55, 0.83], "holm_p": 0.01},
            "HurriedPace": {"n": 44, "median_precision_cosine": 0.41, "bootstrap_ci": [0.20, 0.62], "holm_p": 0.08},
        },
        "healthy_reference_uncertainty": {
            "SelfPace": {"icc_median": 0.64, "icc_reference_interval": [0.57, 0.70]},
            "HurriedPace": {"icc_median": 0.28, "icc_reference_interval": [0.21, 0.35]},
        },
        "claim_boundaries": {
            "short_term_reliability": "NOT_ESTIMABLE",
            "clinical_responsiveness": "NOT_ESTIMABLE",
            "external_full_score_transport": "NOT_ESTIMABLE",
        },
    }


def test_report_preserves_long_interval_and_claim_boundaries():
    text = render_report(synthetic_summary())
    assert "six-plus-month" in text
    assert "short-term" in text
    assert "NOT_ESTIMABLE" in text
    assert "participant" in text.lower()
    assert "healthy-reference" in text.lower()
    assert not find_unsupported_claims(text)


def test_claim_guard_flags_prohibited_overclaims():
    bad = "This clinically validated biomarker tracks disease progression and diagnoses Parkinson disease."
    findings = find_unsupported_claims(bad)
    assert len(findings) >= 3


def test_claim_guard_allows_evidence_bounded_language():
    good = ("The score showed six-plus-month longitudinal instability. Short-term state-controlled "
            "test-retest reliability remains NOT_ESTIMABLE, and this analysis does not establish diagnosis, "
            "treatment response, progression tracking, or external validation.")
    assert not find_unsupported_claims(good)
