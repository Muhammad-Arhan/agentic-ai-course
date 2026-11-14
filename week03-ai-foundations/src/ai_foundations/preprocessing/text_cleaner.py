"""Text preprocessing (Phase 02).

Raw text -> preprocessing -> tokenization -> numerical representation -> model.

Preprocessing is an engineering decision: whether to lowercase or strip
punctuation depends on the problem and the model. For a simple classifier
such as ours it removes noise; for other tasks (sentiment, names, code)
capitalization and punctuation can carry meaning and should be kept.
"""

import re


def clean_text(text: str) -> str:
    """Normalize whitespace, lowercase the text and remove punctuation.

    >>> clean_text("   I NEED HELP!!!   ")
    'i need help'
    """
    if not isinstance(text, str):
        raise TypeError(f"clean_text expects a string, got {type(text).__name__}")

    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)  # drop punctuation (letters, digits, _ stay)
    text = re.sub(r"\s+", " ", text)     # many spaces/tabs/newlines -> one space
    return text.strip()


def clean_texts(texts):
    """Clean every text in a list."""
    return [clean_text(text) for text in texts]
