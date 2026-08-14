from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Protocol, cast

from quant_finbert.config import Settings
from quant_finbert.db import SqlAlchemySentimentRepository
from quant_finbert.domain.finbert import FinBertSentimentAnalyzer

_POSITIVE_WORDS = {
    "beat",
    "bull",
    "bullish",
    "gain",
    "gains",
    "growth",
    "improve",
    "improved",
    "outperform",
    "positive",
    "record",
    "rally",
    "rise",
    "rises",
    "rose",
    "surge",
    "strong",
    "up",
}
_NEGATIVE_WORDS = {
    "bear",
    "bearish",
    "contraction",
    "crash",
    "cut",
    "cuts",
    "decline",
    "drop",
    "falls",
    "layoff",
    "lawsuit",
    "negative",
    "plunge",
    "risk",
    "weak",
    "weaker",
    "warning",
    "warns",
}


@dataclass(frozen=True)
class SentimentResult:
    label: str
    confidence: float
    score: int
    model: str


class SentimentAnalyzer(Protocol):
    def analyze(self, text: str) -> SentimentResult:
        raise NotImplementedError

    def readiness(self) -> tuple[bool, str]:
        raise NotImplementedError


class HeuristicSentimentAnalyzer:
    def __init__(self, model_name: str) -> None:
        self._model_name = model_name

    def analyze(self, text: str) -> SentimentResult:
        normalized_words = {token.strip(".,:;!?()[]{}\"'`").lower() for token in text.split()}
        positive_hits = len(normalized_words & _POSITIVE_WORDS)
        negative_hits = len(normalized_words & _NEGATIVE_WORDS)
        score = positive_hits - negative_hits
        label = "neutral"
        if score > 0:
            label = "positive"
        elif score < 0:
            label = "negative"

        confidence_base = abs(score) / max(len(normalized_words), 1)
        confidence = round(min(0.99, 0.5 + confidence_base), 3)
        return SentimentResult(label=label, confidence=confidence, score=score, model=self._model_name)

    def readiness(self) -> tuple[bool, str]:
        return True, f"sentiment engine ready: {self._model_name}"


class FinBertSentimentAdapter:
    def __init__(self, analyzer: FinBertSentimentAnalyzer) -> None:
        self._analyzer = analyzer

    def analyze(self, text: str) -> SentimentResult:
        payload = self._analyzer.analyze(text)
        return SentimentResult(
            label=str(payload["label"]),
            confidence=float(cast(float, payload["confidence"])),
            score=int(cast(int, payload["score"])),
            model=str(payload["model"]),
        )

    def readiness(self) -> tuple[bool, str]:
        return self._analyzer.readiness()


class SentimentService:
    def __init__(
        self,
        analyzer: SentimentAnalyzer,
        model_name: str,
        repository: SqlAlchemySentimentRepository | None = None,
    ) -> None:
        self._analyzer = analyzer
        self._model_name = model_name
        self._repository = repository

    def readiness(self) -> tuple[bool, str]:
        return self._analyzer.readiness()

    def analyze(
        self,
        text: str,
        source: str | None = None,
        request_id: str | None = None,
        model: str | None = None,
    ) -> dict[str, object]:
        result = self._analyzer.analyze(text)
        response: dict[str, object] = {
            "status": "ok",
            "service": "quant-finbert",
            "model": model or result.model,
            "sentiment": result.label,
            "confidence": result.confidence,
            "score": result.score,
            "text": text,
        }
        if source is not None:
            response["source"] = source
        if request_id is not None:
            response["request_id"] = request_id

        if self._repository is not None:
            self._repository.save_result(
                request_id=request_id,
                source=source,
                model=str(model or result.model),
                text=text,
                sentiment=str(result.label),
                confidence=float(result.confidence),
                score=int(result.score),
                response_payload=json.dumps(response, sort_keys=True),
            )

        return response


def build_sentiment_service(settings: Settings) -> SentimentService:
    repository = SqlAlchemySentimentRepository(settings.database_url)
    repository.init_db()
    analyzer = FinBertSentimentAdapter(FinBertSentimentAnalyzer(settings.model_name))
    return SentimentService(analyzer=analyzer, model_name=settings.model_name, repository=repository)
