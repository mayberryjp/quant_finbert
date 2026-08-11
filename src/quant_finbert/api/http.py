from __future__ import annotations

from bottle import response


def json_response(payload: dict[str, object], status: int = 200) -> dict[str, object]:
    response.content_type = "application/json"
    response.status = status
    return payload


def error_response(
    status: int,
    code: str,
    error: str,
    detail: str | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "status": "error",
        "code": code,
        "error": error,
    }
    if detail is not None:
        payload["detail"] = detail
    return json_response(payload, status=status)
