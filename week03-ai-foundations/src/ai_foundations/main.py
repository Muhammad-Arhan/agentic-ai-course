"""Command-line runner for the Week 3 pipeline.

Run from the project root (virtual environment active). The code lives in src/,
so tell Python where to find it with PYTHONPATH=src (once per terminal: export PYTHONPATH=src):

    PYTHONPATH=src python -m ai_foundations.main all        # every step, start to finish
    PYTHONPATH=src python -m ai_foundations.main classify   # one step
    PYTHONPATH=src python -m ai_foundations.main search --query "Where can I register my courses?"

Steps that need no internet:      sentiment, clean, tokens, sentencepiece, classify
Steps that download a model once: hf-tokens, embeddings, search
"""

import argparse
import sys

from ai_foundations.config import (
    CLASSIFIER_FILE,
    DOCUMENTS_FILE,
    EMBEDDING_MODEL,
    MODELS_DIR,
    TOKENIZER_MODELS,
)
from ai_foundations.embeddings.embedder import Embedder
from ai_foundations.ml.model import (
    COURSE_LABELS,
    COURSE_TEXTS,
    compare_models,
    predict_sentiment,
    train_course_sentiment,
)
from ai_foundations.nlp import classifier, tokenizer
from ai_foundations.preprocessing.text_cleaner import clean_text


def heading(title):
    print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")


# --------------------------------------------------------------------------- #
# Phase 01 - Machine learning: training and inference
# --------------------------------------------------------------------------- #
def step_sentiment(args):
    heading("Phase 01 - ML: training and inference")
    vectorizer, model = train_course_sentiment()  # TRAINING
    print(f"Trained on {len(COURSE_TEXTS)} examples; labels: {sorted(set(COURSE_LABELS))}")

    for text in ["I really love this course", "I really hate this course"]:
        print(f"Inference: {text!r} -> {predict_sentiment(vectorizer, model, text)}")  # INFERENCE

    print("\nPhase 04 - comparing three classifiers (tiny dataset: results are noisy)")
    scores = compare_models()
    print("\nAccuracy summary:", {name: round(score, 2) for name, score in scores.items()})


# --------------------------------------------------------------------------- #
# Phase 02 - Preprocessing
# --------------------------------------------------------------------------- #
def step_clean(args):
    heading("Phase 02 - Text preprocessing")
    examples = [
        "   I NEED HELP!!!   ",
        "Hello,    WORLD!!",
        "What are the admission requirements?",
        "  Mixed\tCASE\nand   spaces...  ",
        "I forgot my password!!!",
    ]
    for text in examples:
        print(f"{text!r:45} -> {clean_text(text)!r}")


# --------------------------------------------------------------------------- #
# Phase 03 - Tokenization
# --------------------------------------------------------------------------- #
def step_tokens(args):
    heading("Phase 03 - Simple tokenizers we write ourselves")

    text = "Agentic AI systems can use tools"
    tokens = tokenizer.tokenize(text)
    print("Word tokens:", tokens, "| count:", len(tokens))

    word = "hello"
    char_vocab = tokenizer.build_char_vocab(word)
    print("Character tokens:", tokenizer.char_tokenize(word))
    print("Character vocab:", char_vocab, "-> IDs:", tokenizer.encode_chars(word, char_vocab))

    vocab = {"<UNK>": 0, "Large": 1, "language": 2, "models": 3, "understand": 4, "text": 5}
    known = "Large language models understand text".split()
    unseen = "Large language models understand images".split()
    print("Word IDs (all known):    ", tokenizer.word_tokens_to_ids(known, vocab))
    print("Word IDs (images=<UNK>): ", tokenizer.word_tokens_to_ids(unseen, vocab))

    print("\nBPE idea: count neighbouring symbol pairs in 'low lower lowest'")
    pairs = tokenizer.count_symbol_pairs("low lower lowest")
    for pair, count in pairs.most_common(4):
        print(f"  {pair}: {count}")
    print("  -> the most frequent pairs get merged first (l+o -> lo, lo+w -> low ...)")


def step_hf_tokens(args):
    heading("Phase 03 - Pretrained tokenizers (BERT WordPiece vs GPT-2 byte-level BPE)")

    bert = tokenizer.load_hf_tokenizer("bert-base-uncased")

    info = tokenizer.inspect_text(bert, "Large language models are powerful.")
    print("Original text:", info["text"])
    print("Tokens:       ", info["tokens"])
    print("Token IDs:    ", info["token_ids"])
    print("Token count:  ", info["token_count"])
    print("Decoded:      ", info["decoded"])

    print("\nSpecial tokens (BERT):")
    for key, value in tokenizer.special_tokens_info(bert).items():
        print(f"  {key}: {value}")

    print("\nSubword tokenization (rare words are split into pieces; ## = continuation):")
    for text in ["Playing with language models.", "unbelievably uncharacteristic"]:
        print(f"  {text!r} -> {bert.tokenize(text)}")

    text = "Artificial intelligence is transforming software engineering."
    print("\nCompare tokenizers on:", text)
    for name, result in tokenizer.compare_tokenizers(text, TOKENIZER_MODELS).items():
        print(f"  {name}: {result['token_count']} tokens -> {result['tokens']}")

    longer = (
        "Artificial intelligence is transforming software engineering "
        "and many other fields."
    )
    counts = tokenizer.characters_vs_tokens(bert, longer)
    print(f"\nCharacters: {counts['characters']} | Tokens: {counts['tokens']}")


def step_sentencepiece(args):
    heading("Phase 03 - SentencePiece: train a tiny tokenizer of our own")
    model_file = tokenizer.train_sentencepiece(
        tokenizer.SENTENCEPIECE_TRAINING_TEXT, MODELS_DIR, vocab_size=50
    )
    print("Saved tokenizer model:", model_file)

    result = tokenizer.sentencepiece_round_trip(
        model_file, "Artificial intelligence is changing software engineering."
    )
    print("Original text:", result["text"])
    print("Pieces:       ", result["pieces"], "  (the ▁ marks the start of a word)")
    print("Token IDs:    ", result["token_ids"])
    print("Token count:  ", result["token_count"])
    print("Decoded:      ", result["decoded"])


# --------------------------------------------------------------------------- #
# Phase 04 - Text classification: raw data -> preprocessing -> model -> label
# --------------------------------------------------------------------------- #
def step_classify(args):
    heading("Phase 04 - Support-message classifier (TF-IDF + Logistic Regression)")

    df = classifier.prepare_dataset()
    print(f"Cleaned {len(df)} messages -> saved to data/processed/")
    print("Messages per category:", df["label"].value_counts().to_dict())

    # 1) EVALUATE: train on 75% of the data, measure on the 25% held back.
    _, accuracy, report = classifier.train_classifier()
    print(f"\nAccuracy on unseen test messages: {accuracy:.2f}")
    print(report)
    print("(Only 4 test messages, so this number is a rough guide, not a precise score.)")

    # 2) FINAL MODEL: retrain on ALL the data, save it, and use it for inference.
    pipeline = classifier.train_final_model()
    classifier.save_model(pipeline)
    print("\nFinal model trained on all messages and saved to:", CLASSIFIER_FILE)
    pipeline = classifier.load_model()  # proves it can be reused without retraining

    messages = [
        "I cannot reset my password",
        "The server is not responding",
        "When does the admission start?",
        "I paid my tuition but it is not shown",
        "Where is my fee voucher?",
        "My login is not working",
    ]
    if args.message:
        messages.append(args.message)

    print("Inference on new messages:")
    for message in messages:
        print(f"  {message!r:45} -> {classifier.predict_message(pipeline, message)}")
    print(
        "\nNot every prediction will be right: with only 16 training messages the model leans on"
        "\nsingle words (for example, 'login' appears only in a technical example). More data helps."
    )


# --------------------------------------------------------------------------- #
# Phase 05 - Embeddings and semantic similarity
# --------------------------------------------------------------------------- #
def step_embeddings(args):
    heading("Phase 05 - Embeddings and semantic similarity")
    print(f"Loading model {EMBEDDING_MODEL} (downloaded once, then cached)...")
    embedder = Embedder()

    anchor = "How do I reset my password?"
    related = "I forgot my password."
    unrelated = "The weather is very hot today."

    vectors = embedder.encode([anchor, related, unrelated])
    print("Embedding shape (sentences x dimensions):", vectors.shape)

    print(f"\nPassword similarity: {embedder.similarity(anchor, related):.4f}")
    print(f"Weather similarity:  {embedder.similarity(anchor, unrelated):.4f}")
    print("-> the related pair should score clearly higher than the unrelated pair.")
    print("   The exact numbers depend on the model; the ORDER is what matters.")


# --------------------------------------------------------------------------- #
# Phase 06 - Semantic search
# --------------------------------------------------------------------------- #
def step_search(args):
    heading("Phase 06 - Semantic search over a small knowledge base")
    documents = [
        line.strip()
        for line in DOCUMENTS_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    print(f"Indexing {len(documents)} documents (embeddings are computed once)...")
    embedder = Embedder()
    embedder.index(documents)

    queries = [
        "Where can I register my courses?",
        "How do I pay my tuition?",
        "When are the exam dates?",
        "Where can I find research papers?",
    ]
    if args.query:
        queries.append(args.query)

    for query in queries:
        print(f"\nQuery: {query}")
        for document, score in embedder.search(query):
            print(f"  {score:.4f} -> {document}")


# --------------------------------------------------------------------------- #
STEPS = {
    "sentiment": step_sentiment,
    "clean": step_clean,
    "tokens": step_tokens,
    "hf-tokens": step_hf_tokens,
    "sentencepiece": step_sentencepiece,
    "classify": step_classify,
    "embeddings": step_embeddings,
    "search": step_search,
}


def run_step(name, args):
    """Run one step; report a failure clearly instead of crashing the whole run."""
    try:
        STEPS[name](args)
        return True
    except Exception as error:  # top-level runner: show the problem, continue with the next step
        print(f"\n[{name}] FAILED: {type(error).__name__}: {error}")
        if isinstance(error, ModuleNotFoundError):
            print("A required package is not installed. Activate the virtual environment (source .venv/bin/activate)")
            print("and follow the setup steps in README.md (PyTorch first, then requirements.txt).")
        elif name in {"hf-tokens", "embeddings", "search"}:
            print("This step downloads a model on first use. Check your internet connection and run it again;")
            print("files that were already downloaded are cached and will not be downloaded twice.")
        return False


def main(argv=None):
    parser = argparse.ArgumentParser(description="Week 3: AI/NLP processing pipeline")
    parser.add_argument("step", choices=[*STEPS, "all"], help="which step to run")
    parser.add_argument("--message", help="extra support message for the classify step")
    parser.add_argument("--query", help="extra search query for the search step")
    args = parser.parse_args(argv)

    names = list(STEPS) if args.step == "all" else [args.step]
    results = {name: run_step(name, args) for name in names}

    failed = [name for name, ok in results.items() if not ok]
    if len(names) > 1:
        heading("Summary")
        for name, ok in results.items():
            print(f"  {'OK    ' if ok else 'FAILED'} {name}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
