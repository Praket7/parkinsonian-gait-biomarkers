from scripts.qa_aan_submission import ABSTRACT, word_count


def test_abstract_is_within_aan_limit():
    assert word_count(ABSTRACT.read_text(encoding="utf-8")) <= 300
