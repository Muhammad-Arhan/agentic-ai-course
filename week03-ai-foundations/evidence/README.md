# Evidence

Put your screenshots and saved output here (commit them to Git).

| File | What to capture |
| --- | --- |
| `run_output.txt` | `PYTHONPATH=src python -m ai_foundations.main all \| tee evidence/run_output.txt` |
| `phase01_ml.png` | the `sentiment` step: training, inference and the model comparison |
| `phase02_cleaning.png` | the `clean` step: before and after |
| `phase03_tokens.png` | the `tokens` and `hf-tokens` steps (tokens, token IDs, decoded text, two tokenizers) |
| `phase03_sentencepiece.png` | the `sentencepiece` step |
| `phase04_classifier.png` | the `classify` step: accuracy and classification report |
| `phase05_similarity.png` | the `embeddings` step: password vs weather scores |
| `phase06_search.png` | the `search` step: at least three queries with ranked documents |
| `tests.png` | `pytest` with all tests passing |
