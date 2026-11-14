"""Machine-learning basics: training vs inference (Phase 01 and Phase 04).

Training  = learning from examples      -> model.fit(X_train, y_train)
Inference = using the learned model     -> model.predict(X_new)
"""

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC

# --------------------------------------------------------------------------- #
# Phase 01: the first classifier (CountVectorizer + Naive Bayes)
# --------------------------------------------------------------------------- #
COURSE_TEXTS = [
    "I love this course",
    "This course is excellent",
    "I hate this course",
    "This course is terrible",
]
COURSE_LABELS = ["positive", "positive", "negative", "negative"]


def train_course_sentiment(texts=COURSE_TEXTS, labels=COURSE_LABELS):
    """TRAINING: learn from the labelled examples. Returns (vectorizer, model)."""
    vectorizer = CountVectorizer()               # text -> word counts
    features = vectorizer.fit_transform(texts)   # numerical representation
    model = MultinomialNB()
    model.fit(features, labels)                  # <- training happens here
    return vectorizer, model


def predict_sentiment(vectorizer, model, text):
    """INFERENCE: use the already-trained model on new text."""
    features = vectorizer.transform([text])      # same vectorizer as in training!
    return str(model.predict(features)[0])       # <- inference happens here


# --------------------------------------------------------------------------- #
# Phase 04: compare three classifiers on a small sentiment dataset
# --------------------------------------------------------------------------- #
SENTIMENT_TEXTS = [
    "I love this product",
    "This product is excellent",
    "Amazing experience",
    "I really enjoyed this",
    "This is fantastic",
    "I hate this product",
    "This product is terrible",
    "Very bad experience",
    "I did not enjoy this",
    "This is horrible",
]
SENTIMENT_LABELS = ["positive"] * 5 + ["negative"] * 5


def compare_models(texts=SENTIMENT_TEXTS, labels=SENTIMENT_LABELS, verbose=True):
    """Train and evaluate several classifiers on the same split.

    Returns {model name: accuracy}. With only 10 examples the test set has 2
    items, so accuracy can only be 0, 0.5 or 1.0: treat it as a demonstration,
    not as proof that one algorithm is better.
    """
    x_train, x_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    vectorizer = TfidfVectorizer()
    x_train_vectors = vectorizer.fit_transform(x_train)  # learn vocabulary on TRAIN only
    x_test_vectors = vectorizer.transform(x_test)        # reuse it on test (no leakage)

    models = {
        "LogisticRegression": LogisticRegression(),
        "LinearSVC": LinearSVC(),
        "MultinomialNB": MultinomialNB(),
    }

    if verbose:
        known_words = set(vectorizer.vocabulary_)
        analyzer = vectorizer.build_analyzer()  # the vectorizer's own tokenizer
        print("Test examples (the models never saw these during training):")
        for text, label in zip(x_test, y_test):
            unseen = [w for w in analyzer(text) if w not in known_words]
            print(f"  {text!r} (true: {label}) | words unseen in training: {unseen}")

    new_text = "I really love this"
    new_vector = vectorizer.transform([new_text])

    scores = {}
    for name, model in models.items():
        model.fit(x_train_vectors, y_train)                 # TRAINING
        predictions = model.predict(x_test_vectors)         # INFERENCE on the test set
        scores[name] = accuracy_score(y_test, predictions)

        if verbose:
            print(f"\n--- {name} ---")
            print("Accuracy:", scores[name])
            print("Predictions:", [str(p) for p in predictions], "| true labels:", list(y_test))
            print(classification_report(y_test, predictions, zero_division=0))
            print(f"New text {new_text!r} -> {str(model.predict(new_vector)[0])}")

    if verbose:
        print(
            "\nNote: a model cannot use words it never saw in training, so a test sentence"
            "\nfull of new words is close to a guess. More (and more varied) data fixes this."
        )
    return scores
