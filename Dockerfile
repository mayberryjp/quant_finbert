FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=America/New_York

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl tzdata \
 && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
 && echo $TZ > /etc/timezone \
 && rm -rf /var/lib/apt/lists/*

ENV HF_HOME=/tmp/huggingface \
  TRANSFORMERS_CACHE=/tmp/huggingface

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir .

RUN useradd -m appuser
USER appuser

EXPOSE 8023

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8023/health || exit 1

CMD ["python", "-m", "quant_finbert"]
