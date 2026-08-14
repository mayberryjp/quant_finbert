import pytest
from webtest import TestApp

from quant_finbert.api.app import create_app
from quant_finbert.domain.sentiment import HeuristicSentimentAnalyzer, SentimentService


@pytest.fixture()
def app() -> TestApp:
    sentiment_service = SentimentService(
        analyzer=HeuristicSentimentAnalyzer("heuristic-v0"),
        model_name="heuristic-v0",
        repository=None,
    )
    return TestApp(create_app(sentiment_service=sentiment_service))
