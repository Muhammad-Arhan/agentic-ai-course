# Week 3: ML, NLP and LLM Foundations

An **AI/NLP processing pipeline**: `data -> preprocessing -> NLP/ML -> representation -> output`.

| Phase | Topic | Code |
| --- | --- | --- |
| 01 | Machine learning: training vs inference | `ml/model.py` |
| 02 | Text preprocessing | `preprocessing/text_cleaner.py` |
| 03 | Tokenization (word, character, BPE idea, WordPiece, SentencePiece) | `nlp/tokenizer.py` |
| 04 | Text classification (TF-IDF + Logistic Regression) and evaluation | `nlp/classifier.py`, `ml/model.py` |
| 05 | Embeddings and semantic similarity | `embeddings/embedder.py` |
| 06 | Semantic search (the idea behind RAG) | `embeddings/embedder.py` |
| 06-07 | LLM foundations, API documentation (concepts) | `STUDY_NOTES.md` |

## Setup (run in this folder)

```bash
# 1) virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2) PyTorch, CPU-only (a few hundred MB). Without this step, sentence-transformers
#    downloads the CUDA build of PyTorch, which is several GB. No GPU is needed.
pip install --resume-retries 10 --retries 10 --timeout 60 torch --index-url https://download.pytorch.org/whl/cpu

# 3) everything else
pip install --resume-retries 10 --retries 10 --timeout 60 -r requirements.txt

# 4) check
python -c "import torch, sklearn, sentence_transformers, sentencepiece; print('Week 3 stack OK, torch', torch.__version__)"
cp .env.example .env     # optional settings
```

Do **not** run `pip freeze > requirements.txt` this week: it would write `torch==...+cpu`,
which cannot be installed from PyPI.

## Run

The code lives in `src/`, so tell Python where to find it. Either set it once per terminal:

```bash
export PYTHONPATH=src
python -m ai_foundations.main all            # every step, start to finish
python -m ai_foundations.main classify       # or one step at a time
python -m ai_foundations.main search --query "Where can I register my courses?"
```

or put `PYTHONPATH=src` in front of each command (`PYTHONPATH=src python -m ai_foundations.main all`).
`pytest` does not need it: `pytest.ini` already points to `src/`.

Steps: `sentiment`, `clean`, `tokens`, `sentencepiece`, `classify` (no internet needed) and
`hf-tokens`, `embeddings`, `search` (download a model the first time, then use the cache).
Save your evidence with: `python -m ai_foundations.main all | tee evidence/run_output.txt`
(with `PYTHONPATH=src` set as above)

## Test

```bash
pytest               # fast, never needs the internet
pytest -m network    # optional: also tests the REAL embedding model (downloads it once)
```

## Where do downloads go?

| What | Where |
| --- | --- |
| Python packages | `.venv/` (this project only) |
| Hugging Face models (BERT/GPT-2 tokenizers, MiniLM embeddings) | `~/.cache/huggingface/` (shared, downloaded once) |
| Files this project creates | `models/` and `data/processed/` (not committed to Git) |

## Structure

```
src/ai_foundations/
  main.py            command-line runner
  config.py          folders and model names
  preprocessing/     text_cleaner.py
  nlp/               tokenizer.py, classifier.py
  ml/                model.py
  embeddings/        embedder.py
data/raw/            support_messages.csv, documents.txt (inputs)
data/processed/      cleaned data (generated)
models/              trained models (generated)
notebooks/           exploration.ipynb
tests/               unit tests
evidence/            your screenshots / saved run output
```

## Notes

- `pypdf`, `python-docx`, `openpyxl`, `fastapi` and `uvicorn` are in `requirements.txt` because the
  lab's install command lists them; they are used in later weeks (loading documents, serving APIs).
- To run the notebook in VS Code: `pip install ipykernel`, install the "Jupyter" extension, then
  choose the `.venv` interpreter as the kernel.
