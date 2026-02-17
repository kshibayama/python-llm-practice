from datetime import datetime
from pydantic import BaseModel, Field

class TicketCreate(BaseModel):
    raw_text: str = Field(min_length=1, max_length=20000)
    source: str = Field(default="web", max_length=50)

class TicketRead(BaseModel):
    id: int
    created_at: datetime
    source: str
    raw_text: str
    status: str

    model_config = {"from_attributes": True}  # SQLAlchemy -> Pydantic変換

