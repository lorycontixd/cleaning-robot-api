FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

# Put the uv-managed virtualenv on PATH so uvicorn (and pytest) resolve directly.
ENV PATH="/app/.venv/bin:$PATH"

COPY . .
RUN uv sync --extra dev

# Fail the build if the test suite doesn't pass.
RUN pytest

EXPOSE 8000

# Readiness probe against the documented health endpoint (slim has no curl).
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import sys, urllib.request; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health', timeout=2).status == 200 else 1)"

CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
