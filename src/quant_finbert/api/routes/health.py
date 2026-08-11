from bottle import Bottle

from quant_finbert.api.http import error_response, json_response
from quant_finbert.domain.sentiment import SentimentService


def register_health_routes(app: Bottle, sentiment_service: SentimentService) -> None:
    @app.get("/health")  # type: ignore[untyped-decorator]
    def health() -> dict[str, object]:
        return json_response({"status": "ok", "service": "quant-finbert"})

    @app.get("/ready")  # type: ignore[untyped-decorator]
    def ready() -> dict[str, object]:
        is_ready, detail = sentiment_service.readiness()
        if not is_ready:
            return error_response(
                503,
                "not_ready",
                "Service not ready",
                detail,
            )
        return json_response(
            {
                "status": "ok",
                "service": "quant-finbert",
                "dependencies": {
                    "sentiment_engine": detail,
                },
            }
        )
