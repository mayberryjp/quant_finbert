# quant-finbert

Self-hosted FinBERT sentiment service for local Docker use.

## Local development

```bash
pip install .[dev]
python -m quant_finbert
```

## Docker

```bash
docker compose up --build
```

The API listens on port `8023` by default.

## Environment

- `API_LISTEN_ADDRESS` default: `0.0.0.0`
- `API_PORT` default: `8023`
- `LOG_LEVEL` default: `INFO`
- `MODEL_NAME` default: `ProsusAI/finbert`
