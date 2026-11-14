import numpy as np

from ai_foundations import main as pipeline_main
from ai_foundations.embeddings.embedder import Embedder


class FakeModel:
    """Tiny stand-in for the sentence-transformer model."""

    WORDS = ("register", "exam", "tuition", "research", "password", "weather")

    def encode(self, texts):
        return np.array([[float(word in text.lower()) for word in self.WORDS] for text in texts])


def test_clean_step_prints_before_and_after(capsys):
    assert pipeline_main.main(["clean"]) == 0
    output = capsys.readouterr().out
    assert "'i need help'" in output


def test_tokens_step_runs_offline(capsys):
    assert pipeline_main.main(["tokens"]) == 0
    output = capsys.readouterr().out
    assert "['agentic', 'ai', 'systems', 'can', 'use', 'tools']" in output
    assert "('l', 'o'): 3" in output


def test_sentiment_step_runs_offline(capsys):
    assert pipeline_main.main(["sentiment"]) == 0
    output = capsys.readouterr().out
    assert "'I really love this course' -> positive" in output


def test_search_step_with_a_fake_model(monkeypatch, capsys):
    monkeypatch.setattr(pipeline_main, "Embedder", lambda: Embedder(model=FakeModel()))
    assert pipeline_main.main(["search", "--query", "Where is the weather report?"]) == 0
    output = capsys.readouterr().out
    assert "Query: Where can I register my courses?" in output
    assert "Query: Where is the weather report?" in output  # the extra --query is used too


def test_embeddings_step_with_a_fake_model(monkeypatch, capsys):
    monkeypatch.setattr(pipeline_main, "Embedder", lambda: Embedder(model=FakeModel()))
    assert pipeline_main.main(["embeddings"]) == 0
    output = capsys.readouterr().out
    assert "Password similarity: 1.0000" in output
    assert "Weather similarity:  0.0000" in output


def test_a_failing_step_is_reported_and_does_not_crash(monkeypatch, capsys):
    def broken(args):
        raise OSError("no internet")

    monkeypatch.setitem(pipeline_main.STEPS, "hf-tokens", broken)
    assert pipeline_main.main(["hf-tokens"]) == 1
    output = capsys.readouterr().out
    assert "FAILED" in output and "no internet" in output
    assert "downloads a model on first use" in output


def test_missing_package_gets_a_helpful_message(monkeypatch, capsys):
    def needs_a_package(args):
        raise ModuleNotFoundError("No module named 'sentence_transformers'")

    monkeypatch.setitem(pipeline_main.STEPS, "embeddings", needs_a_package)
    assert pipeline_main.main(["embeddings"]) == 1
    output = capsys.readouterr().out
    assert "required package is not installed" in output
    assert "README.md" in output
