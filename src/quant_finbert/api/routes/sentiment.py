from bottle import Bottle, request

from quant_finbert.api.http import error_response, json_response
from quant_finbert.domain.finbert import FinBertLoadError
from quant_finbert.domain.sentiment import SentimentService


def register_sentiment_routes(app: Bottle, sentiment_service: SentimentService) -> None:
    @app.post("/sentiment")  # type: ignore[untyped-decorator]
    def sentiment() -> dict[str, object]:
        payload = request.json
        if not isinstance(payload, dict):
            return error_response(
                400,
                "validation_error",
                "Invalid request",
                "Request body must be valid JSON",
            )

        text = payload.get("text")
        if not isinstance(text, str) or not text.strip():
            return error_response(
                422,
                "validation_error",
                "Invalid request",
                "field 'text' is required and must be a non-empty string",
            )

        try:
            result = sentiment_service.analyze(
                text=text,
                source=payload.get("source") if isinstance(payload.get("source"), str) else None,
                request_id=payload.get("request_id")
                if isinstance(payload.get("request_id"), str)
                else None,
                model=payload.get("model") if isinstance(payload.get("model"), str) else None,
            )
        except FinBertLoadError as exc:
            return error_response(503, "not_ready", "Service not ready", str(exc))
        return json_response(result)
