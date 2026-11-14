import pytest

from ai_foundations.preprocessing.text_cleaner import clean_text, clean_texts


def test_instructor_example():
    assert clean_text("   I NEED HELP!!!   ") == "i need help"


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Hello,    WORLD!!", "hello world"),
        ("What are the admission requirements?", "what are the admission requirements"),
        ("  Mixed\tCASE\nand   spaces...  ", "mixed case and spaces"),
        ("I forgot my password!!!", "i forgot my password"),
        ("a - b", "a b"),  # no double space left behind after removing punctuation
        ("Order #123: paid", "order 123 paid"),  # digits are kept
    ],
)
def test_multiple_sentences(raw, expected):
    assert clean_text(raw) == expected


def test_empty_and_punctuation_only():
    assert clean_text("") == ""
    assert clean_text("   ") == ""
    assert clean_text("!!!???") == ""


def test_non_english_letters_are_kept():
    assert clean_text("  میرا پاس ورڈ بھول گیا!  ") == "میرا پاس ورڈ بھول گیا"


def test_rejects_non_string():
    with pytest.raises(TypeError):
        clean_text(None)


def test_clean_texts_list():
    assert clean_texts(["A!", " B "]) == ["a", "b"]
