from fastapi import FastAPI
from app.routers.tickets import router as tickets_router

from pydantic import BaseModel
from logging import getLogger
import logging

app = FastAPI(title="Ticket Demo")

app.include_router(tickets_router)

logger = getLogger(__name__)

@app.get("/health")
def health_check():
    logger.info('health check')
    return { "ok": True }

