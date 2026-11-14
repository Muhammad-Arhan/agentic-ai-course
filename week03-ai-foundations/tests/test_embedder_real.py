"""Tests with the REAL embedding model (needs internet the first time: ~90 MB download).

Skipped by default. Run them on purpose with:   pytest -m network
"""

import pytest

from ai_foundations.embeddings.embedder import Embedder

DOCUMENTS = [
    "Students can register courses through the student portal.",
    "The examination office publishes examination schedules.",
    "The finance office handles tuition fee issues.",
    "The library provides digital research resources.",
]

pytestmark = pytest.mark.network


@pytest.fixture(scope="module")
def embedder():
    return Embedder()


def test_related_sentences_are_more_similar(embedder):
    password = embedder.similarity("How do I reset my password?", "I forgot my password.")
    weather = embedder.similarity("How do I reset my password?", "The weather is very hot today.")
    assert password > weather


def test_course_registration_query_finds_the_registration_document(embedder):
    embedder.index(DOCUMENTS)
    best_document, _ = embedder.search("Where can I register my courses?")[0]
    assert best_document == DOCUMENTS[0]


def test_tuition_query_finds_the_finance_document(embedder):
    embedder.index(DOCUMENTS)
    best_document, _ = embedder.search("How do I pay my tuition?")[0]
    assert best_document == DOCUMENTS[2]
