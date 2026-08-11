from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

@dataclass(frozen=True)
class ModelBundle:
    tokenizer: Any
    model: Any
    device: str
    labels: dict[int, str]


class FinBertLoadError(RuntimeError):
    pass


class FinBertSentimentAnalyzer:
    def __init__(self, model_name: str) -> None:
        self._model_name = model_name

    @property
    def model_name(self) -> str:
        return self._model_name

    @lru_cache(maxsize=1)
    def _load_bundle(self) -> ModelBundle:
        try:
            import torch
            from transformers import AutoModelForSequenceClassification, AutoTokenizer  # type: ignore[attr-defined]
        except Exception as exc:  # pragma: no cover - dependency import failure is environment-specific
            raise FinBertLoadError(f"failed to import FinBERT dependencies: {type(exc).__name__}") from exc

        try:
            tokenizer = AutoTokenizer.from_pretrained(self._model_name)
            model = AutoModelForSequenceClassification.from_pretrained(self._model_name)
        except Exception as exc:
            raise FinBertLoadError(f"failed to load model '{self._model_name}': {type(exc).__name__}") from exc

        model.eval()
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device)
        labels = {index: label.lower() for index, label in model.config.id2label.items()}
        return ModelBundle(tokenizer=tokenizer, model=model, device=device, labels=labels)

    def readiness(self) -> tuple[bool, str]:
        try:
            self._load_bundle()
        except FinBertLoadError as exc:
            return False, str(exc)
        return True, f"sentiment engine ready: {self._model_name}"

    def analyze(self, text: str) -> dict[str, object]:
        try:
            import torch
        except Exception as exc:  # pragma: no cover - dependency import failure is environment-specific
            raise FinBertLoadError(f"failed to import torch: {type(exc).__name__}") from exc

        bundle = self._load_bundle()
        inputs = bundle.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )
        inputs = {key: value.to(bundle.device) for key, value in inputs.items()}
        with torch.no_grad():
            logits = bundle.model(**inputs).logits
            probabilities = torch.softmax(logits, dim=-1)[0]

        top_index = int(torch.argmax(probabilities).item())
        label = bundle.labels.get(top_index, f"label_{top_index}")
        label_map = {
            "positive": "positive",
            "positive_sentiment": "positive",
            "negative": "negative",
            "negative_sentiment": "negative",
            "neutral": "neutral",
        }
        sentiment = label_map.get(label, label)
        confidence = round(float(probabilities[top_index].item()), 3)
        score = int(top_index)
        return {
            "label": sentiment,
            "confidence": confidence,
            "score": score,
            "model": self._model_name,
        }
