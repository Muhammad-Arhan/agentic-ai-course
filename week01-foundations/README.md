# Week 1: Foundations

Agentic AI Systems Engineering, Week 1: a small student-grade application built
as a professional Python project (packages, configuration, JSON, exception
handling, logging, automated tests, Git).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then edit the values in .env
```

## Run

```bash
PYTHONPATH=src python -m agentic_app.main          # enter name and marks
PYTHONPATH=src python -m agentic_app.main --json   # load data/student.json
```

## Test

```bash
pytest
```

## Structure

```
src/agentic_app/   application code (tools, services, utils)
tests/             automated tests
data/              student.json
notebooks/         (empty for now)
```

Secrets live in `.env`, which is never committed.
