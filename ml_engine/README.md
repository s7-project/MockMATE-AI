# MockMATE ML Engine

An independently installable Python package for interview question generation and
candidate-answer evaluation. The React application is not required to develop or test
this package.

## Current rewrite status

- `src/mockmate_ml`: installable package using a `src` layout.
- Pydantic schemas validate generation and evaluation contracts.
- `InterviewService` coordinates generator and evaluator dependencies.
- LLM provider protocol and deterministic fake provider establish a provider-neutral
  integration seam.
- The existing curated question bank remains as a temporary fallback. **Dynamic LLM
  generation is Phase 2 and is not yet implemented in this foundation release.**
- The baseline evaluator currently measures keyword coverage only. It is not a final
  technical-correctness score; semantic and rubric-based evaluation are later phases.
- Transformer, Whisper, OpenCV and MediaPipe dependencies are optional extras and are
  not loaded during package import.

## Setup (from repository root)

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e "./ml_engine[dev]"
```

Install optional capabilities only when needed:

```bash
python -m pip install -e "./ml_engine[gemini]"
python -m pip install -e "./ml_engine[semantic]"
```

## Run tests (from repository root)

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

## Import check

```bash
python -c "import mockmate_ml; from mockmate_ml.services.interview_service import InterviewService; print(mockmate_ml.__version__)"
```

## Backend integration

Install the ML package in the same virtual environment used by FastAPI:

```bash
python -m pip install -e "./ml_engine"
python -m pip install -r backend/requirements.txt
```

Then start the backend from the repository root:

```bash
python -m uvicorn app.main:app --app-dir backend --reload
```

Do not modify `sys.path` or run package source files directly. Use imports from
`mockmate_ml` and invoke Python modules from the repository root.

## Backend adapter test

The backend adapter test is separate because the backend's `app` package is rooted
inside `backend/`:

```bash
cd backend
python -m pytest tests/test_ml_service.py -v
```

The pre-existing full backend test suite also requires all packages in
`backend/requirements.txt` to be installed.
