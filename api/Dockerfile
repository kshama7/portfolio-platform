FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install --prefix=/install \
        "fastapi==0.115.6" "uvicorn[standard]==0.32.1" \
        "pydantic==2.10.3" "pydantic-settings==2.7.0" \
        "numpy==1.26.4" "pandas==2.2.3" "scipy==1.14.1" \
        "pyportfolioopt==1.5.6" "scikit-learn==1.6.0" "yfinance>=1.4.1" \
        "onnxruntime>=1.18" \
        "prometheus-client==0.21.1" "structlog==24.4.0" \
        "httpx==0.28.1" "cachetools==5.5.0"


FROM python:3.11-slim AS runtime

ARG APP_VERSION=0.1.0
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    APP_VERSION=${APP_VERSION} \
    PORT=8000

RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
        curl \
        tini \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r app && useradd -r -g app -u 10001 app

WORKDIR /app

COPY --from=builder /install /usr/local
COPY --chown=app:app app /app/app

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:8000/healthz || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--access-log", "--log-level", "info"]
