from pydantic import BaseModel, Field
from typing import Literal

Category = Literal[
    "auth/login",
    "billing",
    "bug",
    "feature_request",
    "account",
    "other",
]

class TicketLLMOutput(BaseModel):
    summary: str = Field(min_length=1, max_length=600)
    category: Category
    reply_draft: str = Field(min_length=1, max_length=2000)

