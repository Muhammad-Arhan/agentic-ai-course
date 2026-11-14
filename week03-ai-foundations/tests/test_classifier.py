import pandas as pd
import pytest

from ai_foundations.config import SUPPORT_RAW_FILE
from ai_foundations.nlp import classifier
from ai_foundations.preprocessing.text_cleaner import clean_text

CATEGORIES = {"account", "technical", "finance", "admission"}


@pytest.fixture
def clean_file(tmp_path):
    """The raw dataset, cleaned, written to a temporary file (project files stay untouched)."""
    path = tmp_path / "clean.csv"
    classifier.prepare_dataset(SUPPORT_RAW_FILE, path)
    return path


def test_raw_dataset_has_four_balanced_categories():
    df = pd.read_csv(SUPPORT_RAW_FILE)
    assert set(df["label"]) == CATEGORIES
    assert df["label"].value_counts().nunique() == 1  # same number of examples per category


def test_prepare_dataset_cleans_messages(clean_file):
    df = pd.read_csv(clean_file)
    assert len(df) == 16
    assert all(message == clean_text(message) for message in df["message"])
    assert "?" not in " ".join(df["message"])


def test_train_classifier_reports_metrics(clean_file):
    pipeline, accuracy, report = classifier.train_classifier(clean_file)
    assert 0.0 <= accuracy <= 1.0
    assert "precision" in report and "recall" in report and "f1-score" in report
    assert set(pipeline.classes_) == CATEGORIES


def test_final_model_knows_its_training_messages(clean_file):
    pipeline = classifier.train_final_model(clean_file)
    assert classifier.predict_message(pipeline, "I forgot my password") == "account"
    assert classifier.predict_message(pipeline, "The server is down") == "technical"
    assert classifier.predict_message(pipeline, "My tuition payment is not updated") == "finance"
    assert classifier.predict_message(pipeline, "When does admission start?") == "admission"


def test_final_model_on_new_messages(clean_file):
    pipeline = classifier.train_final_model(clean_file)
    assert classifier.predict_message(pipeline, "I cannot reset my password") == "account"
    assert classifier.predict_message(pipeline, "The server is not responding") == "technical"
    assert classifier.predict_message(pipeline, "Where is my fee voucher?") == "finance"


def test_inference_cleans_the_message_like_training(clean_file):
    pipeline = classifier.train_final_model(clean_file)
    shouted = classifier.predict_message(pipeline, "   I FORGOT MY PASSWORD!!!   ")
    plain = classifier.predict_message(pipeline, "i forgot my password")
    assert shouted == plain


def test_prediction_is_a_plain_string(clean_file):
    pipeline = classifier.train_final_model(clean_file)
    assert type(classifier.predict_message(pipeline, "hello")) is str


def test_save_and_load_model_round_trip(clean_file, tmp_path):
    pipeline = classifier.train_final_model(clean_file)
    path = classifier.save_model(pipeline, tmp_path / "models" / "model.joblib")
    assert path.exists()

    reloaded = classifier.load_model(path)
    message = "The website is not loading"
    assert classifier.predict_message(reloaded, message) == classifier.predict_message(pipeline, message)
