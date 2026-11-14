from ai_foundations.ml.model import (
    compare_models,
    predict_sentiment,
    train_course_sentiment,
)


def test_training_then_inference():
    vectorizer, model = train_course_sentiment()
    assert predict_sentiment(vectorizer, model, "I really love this course") == "positive"
    assert predict_sentiment(vectorizer, model, "I really hate this course") == "negative"


def test_prediction_is_a_plain_string():
    vectorizer, model = train_course_sentiment()
    assert type(predict_sentiment(vectorizer, model, "I love this course")) is str


def test_compare_models_returns_a_score_for_each_model():
    scores = compare_models(verbose=False)
    assert set(scores) == {"LogisticRegression", "LinearSVC", "MultinomialNB"}
    assert all(0.0 <= score <= 1.0 for score in scores.values())
