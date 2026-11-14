"""Embeddings, semantic similarity and semantic search (Phases 05 and 06).

An embedding is a vector (a list of numbers) produced by a model, so that texts
with similar MEANING get similar vectors, even if they share no words.

    "How do I reset my password?"  ->  [0.15, -0.72, 0.31, ...]
    "I forgot my password."        ->  [0.17, -0.70, 0.29, ...]   (close)
    "The weather is very hot."     ->  [-0.4,  0.2, 0.9, ...]     (far away)

Semantic search = embed the query, compare it with every document embedding
(cosine similarity), rank the documents by score. This is the idea behind RAG.
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from ai_foundations.config import EMBEDDING_MODEL


def rank_by_similarity(query_vector, document_vectors, documents, top_k=None):
    """Pure function: score every document against the query and sort best first.

    Returns a list of (document, score) pairs.
    """
    scores = cosine_similarity(np.atleast_2d(query_vector), document_vectors)[0]
    ranked = sorted(zip(documents, scores), key=lambda item: item[1], reverse=True)
    ranked = [(document, float(score)) for document, score in ranked]
    return ranked if top_k is None else ranked[:top_k]


class Embedder:
    """Wraps a sentence-transformer model.

    The model is downloaded and loaded the first time it is needed (lazy
    loading), so creating an Embedder is instant. Pass `model=` to use any
    object with an `encode(list_of_texts)` method, for example a fake in tests.
    """

    def __init__(self, model_name: str = EMBEDDING_MODEL, model=None):
        self.model_name = model_name
        self._model = model
        self.documents: list[str] = []
        self.document_vectors = None

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
        return self._model

    # -- embeddings and similarity ------------------------------------------ #
    def encode(self, texts):
        """Texts -> a 2-D array with one embedding (row) per text."""
        return np.asarray(self.model.encode(list(texts)))

    def similarity(self, text_a: str, text_b: str) -> float:
        """Cosine similarity between two texts: about 1 = same meaning, near 0 = unrelated."""
        vectors = self.encode([text_a, text_b])
        return float(cosine_similarity([vectors[0]], [vectors[1]])[0][0])

    # -- semantic search ------------------------------------------------------ #
    def index(self, documents) -> None:
        """Embed and STORE the documents once, so many queries can reuse them."""
        self.documents = list(documents)
        self.document_vectors = self.encode(self.documents)

    def search(self, query: str, top_k=None):
        """Rank the indexed documents by similarity to the query."""
        if self.document_vectors is None:
            raise RuntimeError("Call index(documents) before search().")
        query_vector = self.encode([query])[0]
        return rank_by_similarity(query_vector, self.document_vectors, self.documents, top_k)
