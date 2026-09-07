from __future__ import annotations

import os
from collections.abc import Generator
from datetime import datetime, tzinfo

from sqlalchemy import DateTime, Float, Integer, String, Text, create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

SCHEMA = "finbert"


def local_timezone() -> tzinfo:
    tz_name = os.environ.get("TZ")
    if tz_name:
        from zoneinfo import ZoneInfo

        return ZoneInfo(tz_name)
    return datetime.now().astimezone().tzinfo  # type: ignore[return-value]


def local_now() -> datetime:
    return datetime.now(local_timezone())


def _bind_local_timezone(engine: object) -> None:
    tz_name = os.environ.get("TZ") or str(local_timezone())

    @event.listens_for(engine, "connect")
    def _set_session_timezone(dbapi_connection: object, _connection_record: object) -> None:
        if engine.dialect.name != "postgresql":  # type: ignore[attr-defined]
            return
        cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
        try:
            cursor.execute(f"SET TIME ZONE '{tz_name.replace(chr(39), chr(39) * 2)}'")
        finally:
            cursor.close()


class Base(DeclarativeBase):
    pass


class SentimentRecord(Base):
    __tablename__ = "sentiment_requests"
    __table_args__ = {"schema": SCHEMA}

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
        default=local_now,
        nullable=False,
    )


class SqlAlchemySentimentRepository:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self.engine = _apply_schema(create_engine(database_url))
        _bind_local_timezone(self.engine)
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)

    def init_db(self) -> None:
        init_db(self.engine)

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


def _apply_schema(engine: object) -> object:
    # Postgres keeps the finbert schema; other dialects don't support schemas,
    # so translate it away.
    if engine.dialect.name != "postgresql":  # type: ignore[attr-defined]
        return engine.execution_options(schema_translate_map={SCHEMA: None})  # type: ignore[attr-defined]
    return engine


def init_db(engine: object) -> None:
    if engine.dialect.name == "postgresql":  # type: ignore[attr-defined]
        with engine.begin() as connection:  # type: ignore[attr-defined]
            connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{SCHEMA}"'))
    Base.metadata.create_all(bind=engine)


def get_session() -> Generator[Session, None, None]:
    engine = _apply_schema(create_engine("sqlite:///./quant_finbert.db"))
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    try:
        yield session
    finally:
        session.close()
