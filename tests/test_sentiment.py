def test_sentiment_endpoint_returns_structured_result(app) -> None:
    response = app.post_json(
        "/sentiment",
        {
            "text": "Revenue beat expectations and guidance was raised",
            "source": "news",
            "request_id": "req-123",
        },
    )

    assert response.status_code == 200
    assert response.json["status"] == "ok"
    assert response.json["service"] == "quant-finbert"
    assert response.json["sentiment"] == "positive"
    assert response.json["model"] == "heuristic-v0"
    assert response.json["request_id"] == "req-123"
    assert response.json["source"] == "news"
    assert response.json["confidence"] >= 0.5


def test_sentiment_endpoint_rejects_missing_text(app) -> None:
    response = app.post_json("/sentiment", {}, expect_errors=True)

    assert response.status_code == 422
    assert response.json == {
        "status": "error",
        "code": "validation_error",
        "error": "Invalid request",
        "detail": "field 'text' is required and must be a non-empty string",
    }
