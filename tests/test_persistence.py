from quant_finbert.db import SqlAlchemySentimentRepository, SentimentRecord, init_db
from quant_finbert.domain.sentiment import HeuristicSentimentAnalyzer, SentimentService


def test_sentiment_service_persists_request_and_response(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'quant_finbert.db'}"
    repository = SqlAlchemySentimentRepository(database_url)
    init_db(repository.engine)

    service = SentimentService(
        analyzer=HeuristicSentimentAnalyzer("heuristic-v0"),
        model_name="heuristic-v0",
        repository=repository,
    )

    response = service.analyze(
        text="Strong growth and rally",
        source="news",
        request_id="req-persist-1",
    )

    assert response["status"] == "ok"
    assert response["sentiment"] == "positive"

    with repository.session_factory() as session:
        row = session.query(SentimentRecord).filter_by(request_id="req-persist-1").one()
        assert row.text == "Strong growth and rally"
        assert row.sentiment == "positive"
        assert row.source == "news"
        assert row.model == "heuristic-v0"
