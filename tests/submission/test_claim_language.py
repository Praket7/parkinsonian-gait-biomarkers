from scripts.qa_aan_submission import check


def test_final_report_avoids_unsupported_clinical_claims():
    assert not any("unsupported clinical claim" in error for error in check())
