import re

from scripts.qa_aan_submission import ABSTRACT


def test_canonical_abstract_does_not_advertise_historical_version():
    text = ABSTRACT.read_text(encoding="utf-8")
    assert not re.search(r"\bv3\.2\.4\b", text, re.IGNORECASE)
    assert "outcome-blind" in text.lower()
