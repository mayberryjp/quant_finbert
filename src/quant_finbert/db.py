from __future__ import annotations

from collections.abc import Generator
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class SentimentRecord(Base):
    __tablename__ = "sentiment_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    request_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    model: Mapped[str] = mapped_column(String(255), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    sentiment: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    response_payload: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class SqlAlchemySentimentRepository:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)

    def init_db(self) -> None:
        Base.metadata.create_all(bind=self.engine)

    def save_result(
        self,
        *,
        request_id: str | None,
        source: str | None,
        model: str,
        text: str,
        sentiment: str,
        confidence: float,
        score: int,
        response_payload: str,
    ) -> SentimentRecord:
        record = SentimentRecord(
            request_id=request_id,
            source=source,
            model=model,
            text=text,
            sentiment=sentiment,
            confidence=confidence,
            score=score,
            response_payload=response_payload,
        )
        with self.session_factory() as session:
            session.add(record)
            session.commit()
            session.refresh(record)
        return record


def init_db(engine: object) -> None:
    Base.metadata.create_all(bind=engine)


def get_session() -> Generator[Session, None, None]:
    engine = create_engine("sqlite:///./quant_finbert.db")
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    try:
        yield session
    finally:
        session.close()
