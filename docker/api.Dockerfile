FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY apps/api/pyproject.toml apps/api/.python-version ./
RUN uv sync --no-dev --no-install-project

COPY apps/api ./
RUN uv sync --no-dev --no-install-project

FROM python:3.12-slim AS runner

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:${PATH}"

RUN addgroup --system repomind \
  && adduser --system --ingroup repomind repomind

COPY --from=builder --chown=repomind:repomind /app /app

USER repomind

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
