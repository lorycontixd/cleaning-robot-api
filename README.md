# Cleaning Robot API

A REST service that remotely controls a household cleaning robot: load a
tile map, run cleaning sessions with a `basic` or `premium` robot model,
and export session history as CSV.

All state (loaded map, session history) lives in memory for the process
lifetime. Restarting the service clears it.

## Prerequisites

- **Docker** (for the Docker path), **or**
- **Python 3.12+** and either **[uv](https://docs.astral.sh/uv/)** or **pip** (for the local path).

## Installation

Clone the repository:

```bash
git clone https://github.com/lorycontixd/cleaning-robot-api.git
cd cleaning-robot-api
```

Pick **one** of the setups below.

### Docker

```bash
docker build -t cleaning-robot .
docker run --rm -p 8000:8000 cleaning-robot
```

Note: the Docker build runs the test suite as part of the image build (`RUN pytest` in the [Dockerfile](Dockerfile)), so a failing test fails the build.

### Local — uv (recommended)

```bash
uv sync --extra dev
```

`--extra dev` installs `pytest`, `httpx`, `ruff`, and `mypy` — the tools declared as optional dependencies in [pyproject.toml](pyproject.toml). Without it, `pytest` and the linters will not be available.

### Local — pip

```bash
python -m venv .venv
# Windows:      .venv\Scripts\activate
# Linux/macOS:  source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Run

Start the API on `http://localhost:8000`:

```bash
# uv
uv run uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000

# pip / activated venv
python -m uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

## Verify

Quick health check:

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

Interactive API docs (Swagger UI) are available at [http://localhost:8000/docs](http://localhost:8000/docs). Use them to try the endpoints without writing a client.

### End-to-end smoke test

1. Upload a small text map (`o` = walkable/dirty, `x` = wall):

   ```bash
   printf "oox\noox\n" > sample.txt
   curl -X PUT http://localhost:8000/map -F "file=@sample.txt"
   ```

2. Run a cleaning session:

   ```bash
   curl -X POST http://localhost:8000/clean \
     -H "Content-Type: application/json" \
     -d '{
       "start": {"x": 0, "y": 0},
       "robot_model": "basic",
       "actions": [
         {"direction": "east",  "steps": 1},
         {"direction": "south", "steps": 1}
       ]
     }'
   ```

3. Export the history as CSV:

   ```bash
   curl http://localhost:8000/history
   ```

## Tests and quality checks

```bash
pytest           # test suite
ruff check .     # lint
ruff format .    # format
mypy app         # strict type checking (configured in pyproject.toml)
```

Under `uv`, prefix with `uv run` (e.g. `uv run pytest`).

## Project structure

The project follows a typical FastAPI layout with a strong focus on maintainability and a clear separation of concerns:
- `app/api/` — FastAPI routes, request/response schemas, exception handlers.
- `app/core/` — framework-agnostic domain models and exceptions.
- `app/services/` — orchestration layer. `CleaningService` runs cleaning sessions and coordinates the robot, map, and history.
- `app/maps/` — map parsing (`.txt` and `.json`).
- `app/storage/` — in-process stores for the current map and session history.
- `tests/` — unit and end-to-end tests.

## Design notes

- **Validation at the boundary.** The API layer validates incoming requests with Pydantic. The core layer does not fully trust upstream data and re-checks its own invariants — most unit tests construct domain objects directly and bypass the API, so those checks matter.
- **The map owns the state.** The map is the single source of truth for tile walkability and cleanliness. The robot is a transient agent that operates on the map.
- **Cleanliness persists across sessions.** The map is mutated in place, so a tile cleaned in one session stays clean in the next — until a new map is loaded via `PUT /map`.
