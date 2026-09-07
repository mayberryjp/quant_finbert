"""init quant_finbert sentiment tables

Revision ID: 20260814_000001
Revises:
Create Date: 2026-08-14 00:00:01.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260814_000001"
down_revision = None
branch_labels = None
depends_on = None

SCHEMA = "finbert"


def upgrade() -> None:
    op.execute(f'CREATE SCHEMA IF NOT EXISTS "{SCHEMA}"')
    op.create_table(
        "sentiment_requests",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("request_id", sa.String(length=255), nullable=True),
        sa.Column("source", sa.String(length=255), nullable=True),
        sa.Column("model", sa.String(length=255), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("sentiment", sa.String(length=64), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("response_payload", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )
    op.create_index(op.f("ix_sentiment_requests_request_id"), "sentiment_requests", ["request_id"], unique=False, schema=SCHEMA)
    op.create_index(op.f("ix_sentiment_requests_source"), "sentiment_requests", ["source"], unique=False, schema=SCHEMA)
    op.create_index(op.f("ix_sentiment_requests_sentiment"), "sentiment_requests", ["sentiment"], unique=False, schema=SCHEMA)


def downgrade() -> None:
    op.drop_index(op.f("ix_sentiment_requests_sentiment"), table_name="sentiment_requests", schema=SCHEMA)
    op.drop_index(op.f("ix_sentiment_requests_source"), table_name="sentiment_requests", schema=SCHEMA)
    op.drop_index(op.f("ix_sentiment_requests_request_id"), table_name="sentiment_requests", schema=SCHEMA)
    op.drop_table("sentiment_requests", schema=SCHEMA)
