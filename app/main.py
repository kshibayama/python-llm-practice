from fastapi import FastAPI
from pydantic import BaseModel
from logging import getLogger
import logging

app = FastAPI()
logger = getLogger(__name__)

class Ticket(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health")
def health_check():
    logger.info('health check')
    return { "ok": True }

@app.post("/tickets")
def update_ticekt(ticket: Ticket):
    logger.info('update ticket')
    return ticket
