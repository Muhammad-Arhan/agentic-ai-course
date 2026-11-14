import pytest

from ai_foundations.nlp import tokenizer


# ---- simple tokenizers ------------------------------------------------------ #
def test_word_tokenizer():
    tokens = tokenizer.tokenize("Agentic AI systems can use tools")
    assert tokens == ["agentic", "ai", "systems", "can", "use", "tools"]
    assert len(tokens) == 6


def test_character_tokenizer_and_ids():
    assert tokenizer.char_tokenize("hello") == ["h", "e", "l", "l", "o"]
    vocab = tokenizer.build_char_vocab("hello")
    assert vocab == {"h": 0, "e": 1, "l": 2, "o": 3}
    assert tokenizer.encode_chars("hello", vocab) == [0, 1, 2, 2, 3]


def test_character_not_in_vocab_raises():
    with pytest.raises(KeyError):
        tokenizer.encode_chars("hex", {"h": 0, "e": 1})


def test_unknown_words_map_to_unk():
    vocab = {"<UNK>": 0, "Large": 1, "language": 2, "models": 3, "understand": 4, "text": 5}
    assert tokenizer.word_tokens_to_ids("Large language models understand text".split(), vocab) == [1, 2, 3, 4, 5]
    assert tokenizer.word_tokens_to_ids("Large language models understand images".split(), vocab) == [1, 2, 3, 4, 0]


def test_bpe_pair_counts():
    pairs = tokenizer.count_symbol_pairs("low lower lowest")
    assert pairs[("l", "o")] == 3
    assert pairs[("o", "w")] == 3
    assert pairs[("w", "e")] == 2
    assert pairs[("e", "r")] == 1
    assert pairs.most_common(1)[0][1] == 3


# ---- Hugging Face helpers, tested with a fake tokenizer (no download) -------- #
class FakeBertTokenizer:
    cls_token, sep_token = "[CLS]", "[SEP]"
    cls_token_id, sep_token_id = 101, 102

    def tokenize(self, text):
        return text.lower().replace(".", " .").split()

    def encode(self, text, add_special_tokens=True):
        ids = list(range(1000, 1000 + len(self.tokenize(text))))
        return [101, *ids, 102] if add_special_tokens else ids

    def decode(self, ids):
        return "[CLS] decoded text [SEP]"


def test_inspect_text_includes_special_tokens_in_ids():
    info = tokenizer.inspect_text(FakeBertTokenizer(), "Large models.")
    assert info["tokens"] == ["large", "models", "."]
    assert info["token_ids"][0] == 101 and info["token_ids"][-1] == 102
    assert info["token_count"] == len(info["token_ids"]) == 5
    assert info["decoded"]


def test_special_tokens_info():
    info = tokenizer.special_tokens_info(FakeBertTokenizer())
    assert info["cls_token"] == "[CLS]" and info["sep_token"] == "[SEP]"
    assert info["token_ids"][0] == info["cls_token_id"]


def test_characters_vs_tokens():
    counts = tokenizer.characters_vs_tokens(FakeBertTokenizer(), "ab cd")
    assert counts == {"characters": 5, "tokens": 2}


def test_compare_tokenizers_uses_each_model(monkeypatch):
    monkeypatch.setattr(tokenizer, "load_hf_tokenizer", lambda name: FakeBertTokenizer())
    results = tokenizer.compare_tokenizers("one two", ["model-a", "model-b"])
    assert set(results) == {"model-a", "model-b"}
    assert results["model-a"]["token_count"] == 2


# ---- SentencePiece: real training, no internet needed ------------------------ #
def test_sentencepiece_train_encode_decode(tmp_path):
    pytest.importorskip("sentencepiece")
    model_file = tokenizer.train_sentencepiece(
        tokenizer.SENTENCEPIECE_TRAINING_TEXT, tmp_path, vocab_size=50
    )
    assert model_file.exists()

    text = "Artificial intelligence is changing software engineering."
    result = tokenizer.sentencepiece_round_trip(model_file, text)
    assert result["decoded"] == text
    assert result["token_count"] == len(result["token_ids"]) == len(result["pieces"])
    assert "▁intelligence" in result["pieces"]  # a frequent word becomes one piece


# ---- the helpers also work with a REAL transformers tokenizer (built locally) --- #
def _tiny_bert_tokenizer(tmp_path):
    from transformers import BertTokenizer

    vocab = ["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]",
             "large", "language", "models", "are", "power", "##ful", "."]
    try:  # newer transformers versions take the vocabulary directly
        return BertTokenizer(vocab={token: i for i, token in enumerate(vocab)}, do_lower_case=True)
    except TypeError:  # older versions read it from a file
        vocab_file = tmp_path / "vocab.txt"
        vocab_file.write_text("\n".join(vocab), encoding="utf-8")
        return BertTokenizer(vocab_file=str(vocab_file), do_lower_case=True)


def test_helpers_work_with_a_real_wordpiece_tokenizer(tmp_path):
    pytest.importorskip("transformers")
    bert = _tiny_bert_tokenizer(tmp_path)

    info = tokenizer.inspect_text(bert, "Large language models are powerful.")
    assert info["tokens"] == ["large", "language", "models", "are", "power", "##ful", "."]
    assert info["token_ids"][0] == bert.cls_token_id   # [CLS] added at the start
    assert info["token_ids"][-1] == bert.sep_token_id  # [SEP] added at the end
    assert info["decoded"].startswith("[CLS]") and info["decoded"].endswith("[SEP]")

    special = tokenizer.special_tokens_info(bert, "large models")
    assert special["cls_token"] == "[CLS]" and special["sep_token"] == "[SEP]"
