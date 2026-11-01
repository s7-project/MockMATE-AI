# MockMATE ML Engine

Dataset-driven technical interview question retrieval and baseline answer
evaluation. This package does **not** use an LLM, Gemini, Ollama, or a hosted
generative-AI API.

## Phase 2 implementation

- Versioned JSON dataset with a canonical Pydantic schema.
- 27 starter technical questions across Python, OOP, exception handling,
  functions, FastAPI, web APIs, SQL, and machine learning.
- Dataset provenance fields: source name, URL, and licence declaration.
- JSON dataset loader with schema, duplicate-ID, and duplicate-question checks.
- External JSON/JSONL ingestion utility with conservative field normalization.
- Retrieval filters for topic, difficulty, role, and question type.
- Optional query-term ranking using deterministic metadata/text matching.
- Explicit insufficient-results behaviour; no silent short question sets.
- Stable source dataset IDs plus unique per-interview response IDs.
- Backend adapter passes retrieval filters through to the ML package.

The starter questions are original project-curated examples, not a downloaded
third-party dataset. The `license` field intentionally identifies them as
internal project content; confirm the project's chosen licence before
redistribution. Imported external records must supply source and licence
information; the importer never invents this provenance.

## Setup (from repository root)

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e "./ml_engine[dev]"
```

## Run tests

```bash
python -m pytest ml_engine/tests -v
python -m pytest ml_engine/tests --cov=mockmate_ml --cov-report=term-missing
```

## Quality checks

```bash
ruff check ml_engine/src ml_engine/tests
ruff format --check ml_engine/src ml_engine/tests
mypy ml_engine/src/mockmate_ml
```

## Run a local demo

```bash
python -m mockmate_ml.demo
```

## Ingest an external dataset

Input can be a JSON array, an object containing a `questions` array, or JSONL.
Supported common field aliases include `prompt`/`question`, `answer`/
`reference_answer`, `category`/`topic`, and `keywords`/`key_concepts`.

Every record must include `source_name` and `license`, either in each record
or in the source manifest / CLI arguments. The importer does not infer or assign
legal licences. The CodePrep JSON format is supported, including its difficulty
labels and structured answer objects.

Example for the CodePrep source (download its `data/questions.json` first):

```bash
python -m mockmate_ml.data.ingest codeprep_questions.json \
  ml_engine/src/mockmate_ml/data/datasets/codeprep_questions.json \
  --name "CodePrep Open Interview Questions" \
  --source-name "CodePrep" \
  --source-url "https://github.com/codeprepdev/codeprep-questions" \
  --license "CC-BY-4.0"
```

Attribution: `Questions from CodePrep (https://codeprep.dev), CC-BY-4.0.`
See `ml_engine/DATASET_SOURCES.md` for source notes and review requirements.

```bash
python -m mockmate_ml.data.ingest raw_questions.json \
  ml_engine/src/mockmate_ml/data/datasets/imported_questions.json \
  --name "Reviewed Technical Interview Dataset" \
  --version 1.0.0
```

## Backend integration

Install the package in the same environment as FastAPI:

```bash
python -m pip install -e "./ml_engine"
python -m pip install -r backend/requirements.txt
```

Start the backend from the repository root:

```bash
python -m uvicorn app.main:app --app-dir backend --reload
```

The interview endpoint accepts `topic`, `difficulty`, `count`, optional
`role`, optional `query`, and `allow_partial`. By default, requesting more
questions than are available returns a clear error. Set `allow_partial=true`
only when returning fewer questions is acceptable.

## Architecture

- `schemas/`: request, response, and dataset contracts.
- `data/`: JSON datasets, loading, validation, and ingestion.
- `retrieval/`: deterministic question retrieval and ranking.
- `evaluation/`: current keyword-coverage baseline evaluator.
- `services/`: interview workflow orchestration.

Semantic embedding retrieval and stronger technical answer assessment are
separate future milestones. Current query ranking uses normalized terms and
metadata, not a transformer model.
