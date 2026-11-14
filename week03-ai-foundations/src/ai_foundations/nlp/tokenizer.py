"""Tokenization (Phase 03).

A token is a unit used by a language-processing system. Modern language models
do NOT simply split on spaces: they use SUBWORD tokens.

    text -> tokens -> token IDs -> (embedding matrix) -> vectors

Token IDs are just numbers. They are not embeddings. The model later looks up
a vector for each ID in its embedding matrix.

Sections
    1. Simple tokenizers we write ourselves (word, character, BPE pair counting)
    2. Pretrained tokenizers from Hugging Face (BERT = WordPiece, GPT-2 = byte-level BPE)
    3. SentencePiece (train our own tiny tokenizer)
"""

from collections import Counter
from pathlib import Path

# --------------------------------------------------------------------------- #
# 1. Simple tokenizers
# --------------------------------------------------------------------------- #


def tokenize(text: str) -> list[str]:
    """Introductory word tokenizer: lowercase, then split on whitespace."""
    return text.lower().split()


def char_tokenize(text: str) -> list[str]:
    """Character-level tokenization: every character is a token."""
    return list(text)


def build_char_vocab(text: str) -> dict[str, int]:
    """Give each distinct character an ID, in order of first appearance."""
    vocab: dict[str, int] = {}
    for char in text:
        if char not in vocab:
            vocab[char] = len(vocab)
    return vocab


def encode_chars(text: str, vocab: dict[str, int]) -> list[int]:
    """Characters -> token IDs. (Raises KeyError for a character not in vocab.)"""
    return [vocab[char] for char in text]


def word_tokens_to_ids(tokens: list[str], vocab: dict[str, int]) -> list[int]:
    """Word tokens -> IDs. A word missing from the vocabulary becomes <UNK>."""
    unknown_id = vocab["<UNK>"]
    return [vocab.get(token, unknown_id) for token in tokens]


def count_symbol_pairs(text: str) -> Counter:
    """The first step of BPE (Byte Pair Encoding).

    Start with single characters, then count how often each neighbouring pair
    occurs. BPE repeatedly merges the most frequent pair into a new token,
    e.g. l + o -> lo, then lo + w -> low.
    """
    pairs: Counter = Counter()
    for word in text.split():
        symbols = list(word)
        for left, right in zip(symbols, symbols[1:]):
            pairs[(left, right)] += 1
    return pairs


# --------------------------------------------------------------------------- #
# 2. Pretrained Hugging Face tokenizers
#    (the first call downloads a few small files, then they are cached)
# --------------------------------------------------------------------------- #


def load_hf_tokenizer(model_name: str):
    """Load a pretrained tokenizer, e.g. "bert-base-uncased" or "gpt2"."""
    from transformers import AutoTokenizer  # imported here so the rest works without it

    return AutoTokenizer.from_pretrained(model_name)


def inspect_text(tokenizer, text: str) -> dict:
    """Tokens, token IDs, token count and decoded text for one sentence.

    The IDs include special tokens when the tokenizer uses them
    (BERT adds [CLS] at the start and [SEP] at the end).
    """
    tokens = tokenizer.tokenize(text)
    token_ids = tokenizer.encode(text, add_special_tokens=True)
    return {
        "text": text,
        "tokens": tokens,
        "token_ids": token_ids,
        "token_count": len(token_ids),
        "decoded": tokenizer.decode(token_ids),
    }


def compare_tokenizers(text: str, model_names: list[str]) -> dict[str, dict]:
    """The same text can produce a different number of tokens in each tokenizer."""
    results = {}
    for name in model_names:
        tokenizer = load_hf_tokenizer(name)
        token_ids = tokenizer.encode(text, add_special_tokens=False)
        results[name] = {
            "tokens": tokenizer.tokenize(text),
            "token_count": len(token_ids),
        }
    return results


def special_tokens_info(tokenizer, text: str = "Hello world") -> dict:
    """Show the special tokens a tokenizer adds around the text."""
    return {
        "tokens": tokenizer.tokenize(text),
        "token_ids": tokenizer.encode(text, add_special_tokens=True),
        "cls_token": tokenizer.cls_token,
        "sep_token": tokenizer.sep_token,
        "cls_token_id": tokenizer.cls_token_id,
        "sep_token_id": tokenizer.sep_token_id,
    }


def characters_vs_tokens(tokenizer, text: str) -> dict:
    """Compare text length in characters with its length in tokens."""
    token_ids = tokenizer.encode(text, add_special_tokens=False)
    return {"characters": len(text), "tokens": len(token_ids)}


# --------------------------------------------------------------------------- #
# 3. SentencePiece (unigram): train a tiny tokenizer of our own
# --------------------------------------------------------------------------- #

SENTENCEPIECE_TRAINING_TEXT = """\
I love artificial intelligence.
Artificial intelligence is changing software engineering.
Large language models process text using tokens.
Tokenization converts text into smaller units.
Machine learning is an important field of computer science.
Natural language processing allows computers to understand text.
Python is widely used for artificial intelligence.
Students are learning about large language models.
"""


def train_sentencepiece(
    training_text: str,
    output_dir: Path,
    model_prefix: str = "my_tokenizer",
    vocab_size: int = 50,
) -> Path:
    """Train a SentencePiece unigram tokenizer. Returns the path of the .model file."""
    import sentencepiece as spm

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    training_file = output_dir / f"{model_prefix}_training.txt"
    training_file.write_text(training_text, encoding="utf-8")

    prefix = output_dir / model_prefix
    spm.SentencePieceTrainer.train(
        input=str(training_file),
        model_prefix=str(prefix),
        vocab_size=vocab_size,
        model_type="unigram",
        character_coverage=1.0,
        minloglevel=2,  # keep the training log quiet
    )
    return prefix.with_suffix(".model")


def sentencepiece_round_trip(model_file: Path, text: str) -> dict:
    """Encode text to pieces and IDs, then decode it back."""
    import sentencepiece as spm

    processor = spm.SentencePieceProcessor(model_file=str(model_file))
    pieces = processor.encode(text, out_type=str)  # the "▁" marks a word start
    token_ids = processor.encode(text, out_type=int)
    return {
        "text": text,
        "pieces": pieces,
        "token_ids": token_ids,
        "token_count": len(token_ids),
        "decoded": processor.decode(token_ids),
    }
