from bottle import Bottle

from quant_finbert.api.http import error_response
from quant_finbert.api.routes.health import register_health_routes
from quant_finbert.api.routes.sentiment import register_sentiment_routes
from quant_finbert.config import settings
from quant_finbert.domain.sentiment import SentimentService, build_sentiment_service


def create_app(sentiment_service: SentimentService | None = None) -> Bottle:
    if sentiment_service is None:
        sentiment_service = build_sentiment_service(settings)
    app = Bottle()

    @app.error(404)  # type: ignore[untyped-decorator]
    def not_found(_error: object) -> dict[str, object]:
        return error_response(404, "not_found", "Not found")

    @app.error(405)  # type: ignore[untyped-decorator]
    def method_not_allowed(_error: object) -> dict[str, object]:
        return error_response(405, "method_not_allowed", "Method not allowed")

    @app.error(500)  # type: ignore[untyped-decorator]
    def internal_error(_error: object) -> dict[str, object]:
        return error_response(500, "internal_error", "Internal server error")

    register_health_routes(app, sentiment_service)
    register_sentiment_routes(app, sentiment_service)
    return app
