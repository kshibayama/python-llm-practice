from datetime import datetime
from pydantic import BaseModel

class ResultRead(BaseModel):
    id: int
    ticket_id: int
    summary: str
    category: str
    reply_draft: str
    model: str
    prompt_version: str
    created_at: datetime

    model_config = {"from_attributes": True}

