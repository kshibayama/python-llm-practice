import logging
import os
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.db.models import Ticket, Result
from app.schemas.ticket import TicketCreate, TicketRead
from app.schemas.result import ResultRead

from app.llm.ticket_processor import analyze_ticket
from app.llm.client import OPENAI_MODEL, PROMPT_VERSION

router = APIRouter(prefix="/tickets", tags=["tickets"])

logger = logging.getLogger(__name__)

@router.post("", response_model=TicketRead)
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)):
    ticket = Ticket(
        raw_text=payload.raw_text,
        source=payload.source,
        status="new",
    )
    db.add(ticket)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(ticket)
    return ticket

@router.get("/{ticket_id}", response_model=TicketRead)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    stmt = select(Ticket).where(Ticket.id == ticket_id)
    ticket = db.execute(stmt).scalar_one_or_none()
    if ticket is None:
        raise HTTPException(status_code=404, detail="ticket not found")
    return ticket


@router.get("/{ticket_id}/result", response_model=ResultRead)
def get_result(ticket_id: int, db: Session = Depends(get_db)):
    stmt = select(Result).where(Result.ticket_id == ticket_id)
    result = db.execute(stmt).scalar_one_or_none()
    if result is None:
        raise HTTPException(status_code=404, detail="result not found")
    return result


@router.post("/{ticket_id}/process", response_model=ResultRead)
def process_ticket(
    ticket_id: int,
    force: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    # ticket取得
    ticket = db.execute(select(Ticket).where(Ticket.id == ticket_id)).scalar_one_or_none()
    if ticket is None:
        raise HTTPException(status_code=404, detail="ticket not found")

    # 既に結果がある場合は冪等に返す（force=true なら更新する）
    existing = db.execute(select(Result).where(Result.ticket_id == ticket_id)).scalar_one_or_none()
    if existing is not None and not force:
        return existing

    # ステータス更新
    ticket.status = "processing"
    db.add(ticket)
    db.commit()

    try:

        analysis, request_id = analyze_ticket(ticket.raw_text)

        summary = analysis.summary
        category = analysis.category
        reply_draft = analysis.reply_draft

        if existing is None:
            result = Result(
                ticket_id=ticket_id,
                summary=summary,
                category=category,
                reply_draft=reply_draft,
                model=OPENAI_MODEL,
                prompt_version=PROMPT_VERSION,
            )
            db.add(result)
        else:
            existing.summary = summary
            existing.category = category
            existing.reply_draft = reply_draft
            existing.model = "dummy"
            existing.prompt_version = "v1"
            result = existing

        ticket.status = "done"
        db.add(ticket)

        db.commit()
        db.refresh(result)
        return result

    except Exception as e:
        db.rollback()
        logger.exception('processing failed', extra={"ticket_id": ticket_id})

        # 開発中だけ detail に例外文字列を返す（本番では隠す）
        if os.getenv("DEBUG", "1") == "1":
            raise HTTPException(status_code=500, detail=f"processing failed: {type(e).__name__}: {e}")

        # 失敗を記録（最低限）
        ticket = db.execute(select(Ticket).where(Ticket.id == ticket_id)).scalar_one_or_none()
        if ticket is not None:
            ticket.status = "failed"
            db.add(ticket)
            db.commit()
        raise HTTPException(status_code=500, detail="processing failed")
