from scripts.check_aan_submission_claims import check_values


def test_submission_values_match_frozen_aggregates():
    assert check_values() == []
