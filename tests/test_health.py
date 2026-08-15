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


def test_cors_headers_allow_any_origin(app) -> None:
    response = app.get("/health", headers={"Origin": "https://example.com"})

    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "*"


def test_cors_preflight_is_supported(app) -> None:
    response = app.options(
        "/sentiment",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )

    assert response.status_code == 204
    assert response.headers["Access-Control-Allow-Origin"] == "*"
    assert "POST" in response.headers["Access-Control-Allow-Methods"]
