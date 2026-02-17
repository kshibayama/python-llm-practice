from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    source: Mapped[str] = mapped_column(String(50), default="web", nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="new", nullable=False)

    # 1 ticket = 1 result
    result: Mapped[Optional["Result"]] = relationship(
        back_populates="ticket",
        uselist=False,
        cascade="all, delete-orphan",
    )


class Result(Base):
    __tablename__ = "results"
    __table_args__ = (
        UniqueConstraint("ticket_id", name="uq_results_ticket_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("tickets.id"), nullable=False
    )

    summary: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    reply_draft: Mapped[str] = mapped_column(Text, nullable=False)

    model: Mapped[str] = mapped_column(String(100), nullable=False, default="dummy")
    prompt_version: Mapped[str] = mapped_column(String(50), nullable=False, default="v1")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    ticket: Mapped["Ticket"] = relationship(back_populates="result")

