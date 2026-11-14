"""Support-message classifier (Phase 04): TF-IDF + Logistic Regression.

Pipeline:  input text -> text representation (TF-IDF) -> classifier -> category
Categories: account, technical, finance, admission.
"""

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from ai_foundations.config import (
    CLASSIFIER_FILE,
    SUPPORT_CLEAN_FILE,
    SUPPORT_RAW_FILE,
)
from ai_foundations.preprocessing.text_cleaner import clean_text


def prepare_dataset(raw_path=SUPPORT_RAW_FILE, clean_path=SUPPORT_CLEAN_FILE):
    """data/raw -> preprocessing -> data/processed. Returns the cleaned DataFrame."""
    df = pd.read_csv(raw_path)
    df["message"] = df["message"].map(clean_text)
    clean_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(clean_path, index=False)
    return df


def load_dataset(path=SUPPORT_CLEAN_FILE):
    """Return (messages, labels) from a CSV with `message` and `label` columns."""
    df = pd.read_csv(path)
    return df["message"], df["label"]


def build_pipeline():
    """Representation + classifier in one object, so they always travel together."""
    return Pipeline(
        [
            ("tfidf", TfidfVectorizer()),
            ("classifier", LogisticRegression(max_iter=1000)),
        ]
    )


def train_classifier(path=SUPPORT_CLEAN_FILE, test_size=0.25, random_state=42):
    """TRAINING: split the data, fit the pipeline, evaluate on unseen data.

    Returns (pipeline, accuracy, report_text).
    """
    texts, labels = load_dataset(path)

    x_train, x_test, y_train, y_test = train_test_split(
        texts, labels, test_size=test_size, random_state=random_state, stratify=labels
    )

    pipeline = build_pipeline()
    pipeline.fit(x_train, y_train)

    predictions = pipeline.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)
    report = classification_report(y_test, predictions, zero_division=0)
    return pipeline, accuracy, report


def train_final_model(path=SUPPORT_CLEAN_FILE):
    """Train the model we will actually USE, on ALL the labelled data.

    Standard workflow:
      1. train_classifier()   -> hold some data back to MEASURE how good the approach is
      2. train_final_model()  -> once happy, retrain on everything so no example is wasted
    (With only 16 messages, wasting 4 of them noticeably weakens the model.)
    """
    texts, labels = load_dataset(path)
    pipeline = build_pipeline()
    pipeline.fit(texts, labels)
    return pipeline


def predict_message(pipeline, message):
    """INFERENCE: classify one new message.

    The message is cleaned exactly like the training data was. If training
    text was cleaned and inference text is not, the model sees different input
    than it learned from.
    """
    return str(pipeline.predict([clean_text(message)])[0])


def save_model(pipeline, path=CLASSIFIER_FILE):
    """Save the trained pipeline so it can be reused without retraining."""
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, path)
    return path


def load_model(path=CLASSIFIER_FILE):
    """Load a pipeline saved by save_model().

    Only load model files you created yourself: joblib files can run code
    when opened, so a file from an untrusted source is a security risk.
    """
    return joblib.load(path)
