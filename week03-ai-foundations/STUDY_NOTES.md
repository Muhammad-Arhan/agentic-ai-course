# Week 3 study notes (read before your viva)

## 1. Machine learning (Phase 01)
- Traditional software: **you write the rule** (`marks >= 50`). Machine learning: **the computer learns the rule from examples**.
- Vocabulary: *dataset* (all examples), *sample* (one example), *feature* (information the model uses), *label* (the expected answer), *model* (what was learned).
- **Training** = learning from labelled examples: `model.fit(X_train, y_train)`.
  **Inference** = using the trained model on new input: `model.predict(X_new)`.
- A model cannot read English. Text must become numbers first: `text -> CountVectorizer/TF-IDF -> numbers -> model -> prediction`.
- Always use the **same** vectorizer for training and inference (`transform`, not `fit_transform`, on new text).

## 2. Preprocessing (Phase 02)
- Why: raw text has noise (extra spaces, inconsistent capitals, punctuation). Cleaning makes equal things look equal, so the model needs fewer examples.
- Our `clean_text`: lowercase, remove punctuation, collapse whitespace, strip.
- **It is an engineering decision, not a rule.** Do not always remove everything: punctuation, capitals and word boundaries can carry meaning (sentiment, names, code).
- Clean the text the same way at training time and at inference time.

## 3. Tokenization (Phase 03)
- A **token** is a unit a language system works with. Modern models do not just split on spaces: they use **subword** tokens.
- Levels: character ("h","e","l"...), word, subword.
- **Subword** tokenizers split rare words into known pieces (`unhappiness -> un + happiness`), so there is no endless vocabulary and few unknown words.
- **BPE (Byte Pair Encoding):** start with characters, repeatedly merge the most frequent neighbouring pair (`l+o -> lo`, `lo+w -> low`). Our `count_symbol_pairs` is its first step.
- **WordPiece** (BERT): `playing -> play + ##ing`; `##` means "continues the previous word".
- **SentencePiece / Unigram:** works on raw text without pre-splitting by spaces; `▁` marks a word start.
- **Byte-level BPE** (GPT-style): works on bytes, so Urdu, emoji, code and URLs all work.
- **Special tokens:** BERT adds `[CLS]` at the start and `[SEP]` at the end; `[UNK]` = unknown, `[PAD]` = padding. They are added by the tokenizer, so token counts include them.
- **Token IDs are not embeddings.** `"Hello world" -> [101, 7592, 2088, 102]` are only IDs. The model looks each ID up in an **embedding matrix** to get a vector.
- Different tokenizers give different token counts for the same text. This matters for LLM **cost and context limits**.

## 4. Classification and evaluation (Phase 04)
- **TF-IDF** gives high weight to words that distinguish documents (`love`, `hate`) and low weight to words that appear everywhere (`product`).
- Metrics: **accuracy** = share of correct predictions. **Precision** = of the messages predicted `account`, how many really were. **Recall** = of all real `account` messages, how many were found. **F1** = combines precision and recall.
- Traditional ML: trained for *your* labels, fast, cheap. LLM zero-shot: no training, you only write a prompt with the categories.
- **Tiny data lesson (seen in our own output):**
  - The 10-sentence sentiment test set had words never seen in training, so two models scored 0.0. A model cannot use a word it never saw.
  - Evaluate on held-out data, then retrain the **final** model on **all** the data (`train_final_model`).
  - With 4 test messages, one wrong prediction changes accuracy by 25 points. Treat the score as a rough guide.

## 5. Embeddings and semantic similarity (Phase 05)
- An **embedding** is a vector produced by a model so that texts with similar **meaning** get similar vectors.
- **Word counts** (CountVectorizer/TF-IDF) match *words*: "reset my credentials" and "I forgot my password" share almost no words, so they look unrelated.
  **Embeddings** capture *meaning*: they look similar.
- **Cosine similarity** measures the angle between two vectors: about 1 = same direction (similar meaning), about 0 = unrelated.
- Interpreting scores: only the **relative order** matters ("password pair" > "weather pair"). The absolute numbers depend on the model, so do not compare scores between different models.

## 6. Semantic search (Phase 06)
```
documents -> embeddings (computed once, stored)
query     -> embedding -> cosine similarity with every document -> rank -> top results
```
- This is the core of **RAG**: an agent does not send thousands of documents to the LLM, it retrieves only the relevant ones.

## 7. LLM foundations (Phase 06 slides)
- Application view: `Application -> Model -> Input/Context -> Inference -> Output`. Sending input to an already-trained model is **inference**.
- **Context window:** the amount of context a model can process per request. It is **bounded**. Agents accumulate instructions, history, tool results and retrieved documents, so context must be managed.
- **Hallucination:** fluent output that is unsupported or wrong. **Fluent is not the same as correct.** In agents a wrong assumption can trigger a wrong *action*, hence validation, grounding, tool constraints, evaluation, guardrails, human approval, observability.

### Decision activity: which tool fits?
| Scenario | Best fit | Why |
| --- | --- | --- |
| Research a question, decide what information is needed, search, evaluate, search again, answer | **Agent** | It decides its own next steps and loops until done |
| Generate a natural-language summary of a 30-page report | **LLM application** | One input, generated text out |
| Every morning: read a fixed data source, generate a report, save it, email the manager | **Workflow** | Fixed, predictable steps (an LLM may be one step) |
| Decide whether a financial transaction is fraudulent | **Machine learning** | A classification problem on labelled data |

## 8. API documentation (Phase 07)
To integrate any API reliably (a payment API, an LLM provider) you must find its **contract**. Example, our own Week 2 service:

| Item | Example |
| --- | --- |
| Base URL | `http://127.0.0.1:8000` |
| Endpoint | `/users/{user_id}` |
| HTTP method | `GET` |
| Parameters | `user_id` (path, integer, 1 or greater) |
| Headers | `Accept: application/json` |
| Authentication | none (a protected API: `Authorization: Bearer <key>`) |
| Request body | none for GET (POST/PUT: `name`, `username`, `email`) |
| Response | `200` + `{"id", "name", "username", "email"}` |
| Errors | `404`, `422`, `429` (+ `Retry-After`), `502`, `504` |

## 9. Things I noticed in the lab material (worth mentioning to your instructor)
- **Phase 06 slide 4** says the answer for the query *"Where can I register my courses?"* is **Document 2**. Document 2 is the examination schedule; the correct best match is **Document 1** (course registration). The solution text looks copied from the password example. Our code and the optional real-model test (`pytest -m network`) confirm Document 1.
- **Week 03 Code 09** contains `**name**` / `**main**`, a formatting accident. Python needs `__name__` and `"__main__"`.
- **Phase 04 Code 02** assigns `texts`/`labels` twice (the first, "fees" version, is overwritten) and assigns `model =` four times in a row. It looks like a model *comparison* that was left unfinished; `compare_models()` does it properly.
- **Code 06** (SentencePiece) writes files into whatever folder you run from. Here they go to `models/`.
