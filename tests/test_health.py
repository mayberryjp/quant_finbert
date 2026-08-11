def test_health_endpoint_returns_ok(app) -> None:
    response = app.get("/health")

    assert response.status_code == 200
    assert response.json == {"status": "ok", "service": "quant-finbert"}


def test_ready_endpoint_returns_ok(app) -> None:
    response = app.get("/ready")

    assert response.status_code == 200
    assert response.json == {
        "status": "ok",
        "service": "quant-finbert",
        "dependencies": {"sentiment_engine": "sentiment engine ready: heuristic-v0"},
    }
