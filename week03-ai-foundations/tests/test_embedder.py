import numpy as np
import pytest

from ai_foundations.embeddings.embedder import Embedder, rank_by_similarity

# Each dimension = one "topic". A fake model, so tests need no download.
TOPICS = [
    ("course", "register", "portal"),
    ("exam", "schedule"),
    ("fee", "tuition", "finance", "pay"),
    ("library", "research"),
    ("password", "login", "reset", "forgot"),
    ("weather", "hot"),
]


class FakeModel:
    def __init__(self):
        self.encode_calls = 0

    def encode(self, texts):
        self.encode_calls += 1
        return np.array(
            [[float(any(word in text.lower() for word in topic)) for topic in TOPICS] for text in texts]
        )


DOCUMENTS = [
    "Students can register courses through the student portal.",
    "The examination office publishes examination schedules.",
    "The finance office handles tuition fee issues.",
    "The library provides digital research resources.",
]


@pytest.fixture
def embedder():
    return Embedder(model=FakeModel())


def test_encode_returns_one_row_per_text(embedder):
    vectors = embedder.encode(["a", "b", "c"])
    assert vectors.shape == (3, len(TOPICS))


def test_related_sentences_score_higher_than_unrelated(embedder):
    related = embedder.similarity("How do I reset my password?", "I forgot my password.")
    unrelated = embedder.similarity("How do I reset my password?", "The weather is very hot today.")
    assert related == pytest.approx(1.0)
    assert unrelated == pytest.approx(0.0)
    assert related > unrelated


def test_search_ranks_the_relevant_document_first(embedder):
    embedder.index(DOCUMENTS)
    results = embedder.search("Where can I register my courses?")
    assert results[0][0] == DOCUMENTS[0]
    assert [score for _, score in results] == sorted([score for _, score in results], reverse=True)


@pytest.mark.parametrize(
    "query, expected_index",
    [
        ("Where can I register my courses?", 0),
        ("When is the exam schedule published?", 1),
        ("How do I pay my tuition?", 2),
        ("Where can I find research papers?", 3),
    ],
)
def test_four_different_queries(embedder, query, expected_index):
    embedder.index(DOCUMENTS)
    assert embedder.search(query)[0][0] == DOCUMENTS[expected_index]


def test_top_k_limits_results(embedder):
    embedder.index(DOCUMENTS)
    assert len(embedder.search("exam", top_k=2)) == 2


def test_documents_are_embedded_once_and_reused(embedder):
    embedder.index(DOCUMENTS)
    calls_after_indexing = embedder.model.encode_calls
    embedder.search("one query")
    embedder.search("another query")
    assert embedder.model.encode_calls == calls_after_indexing + 2  # one per query, not per document


def test_search_before_index_is_an_error(embedder):
    with pytest.raises(RuntimeError):
        embedder.search("anything")


def test_model_is_not_loaded_until_needed():
    assert Embedder()._model is None  # creating an Embedder does not download anything


def test_rank_by_similarity_is_a_pure_function():
    vectors = np.array([[1.0, 0.0], [0.0, 1.0], [0.7, 0.7]])
    ranked = rank_by_similarity([1.0, 0.0], vectors, ["x-axis", "y-axis", "diagonal"])
    assert [doc for doc, _ in ranked] == ["x-axis", "diagonal", "y-axis"]
