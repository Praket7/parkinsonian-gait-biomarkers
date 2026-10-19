from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REMOVED_PUBLIC_ARTIFACTS = (
    "report/AAN_FINAL_REPORT.md",
    "report/AAN_bibliography.md",
    "report/AAN_prior_work_table.md",
    "report/AUTHORSHIP_AND_ASSISTANCE.md",
    "report/HISTORICAL_REPORTS.md",
    "docs/analysis_deviations.md",
    "docs/preregistration.md",
    "docs/qa_audit.md",
    "docs/v3_2_analysis_freeze.md",
    "docs/v4_1_analysis_freeze.md",
    "docs/v4_1_preregistration.md",
    "docs/v4_1_validation_questions.md",
    "docs/v4_2_analysis_freeze.md",
    "docs/v4_2_preregistration.md",
    "docs/v4_2_reporting_addendum.md",
    "docs/v4_2_walkway_reconstruction.md",
    "docs/v4_3_h4_reconstruction.md",
    "docs/v4_4_measurement_protocol.md",
    "docs/v4_6_preregistration.md",
    "docs/v4_6_runbook.md",
    "docs/v4_analysis_freeze.md",
    "docs/v4_feature_dictionary.md",
    "docs/v4_preregistration.md",
    "results/v4/frozen/AAN_v4_report.md",
    "results/v4_1/frozen/AAN_v4_1_report.md",
    "results/v4_2/frozen/AAN_v4_2_report.md",
    "results/v4_4/AAN_v4_4_report.md",
    "results/v4_5/AAN_v4_5_report.md",
)


def test_internal_and_historical_narrative_artifacts_are_not_published():
    remaining = [path for path in REMOVED_PUBLIC_ARTIFACTS if (ROOT / path).exists()]
    assert not remaining, f"unessential public artifacts remain: {remaining}"
