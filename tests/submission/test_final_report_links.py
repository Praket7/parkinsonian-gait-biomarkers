from scripts.qa_aan_submission import check


def test_final_report_links_and_figures_resolve():
    errors = check()
    assert not [error for error in errors if "broken link" in error or "missing final figure" in error]
