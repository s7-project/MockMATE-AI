# MockMATE

MockMATE is an AI-assisted mock interview project with a React frontend, FastAPI
backend, and independently installable Python ML engine.

## ML engine development

See [`ml_engine/README.md`](ml_engine/README.md) for environment setup, package
installation, testing, import checks and quality commands.

The ML engine is developed independently of the frontend. Install it into the same
virtual environment as the backend with `python -m pip install -e "./ml_engine"`.
