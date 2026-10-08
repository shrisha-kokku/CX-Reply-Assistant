# Shapes of the data the API accepts. FastAPI rejects anything that doesn't match.
from typing import Literal
from pydantic import BaseModel, Field


class MessageIn(BaseModel):
    sender: Literal["customer", "agent"]
    body: str = Field(min_length=1, max_length=2000)


class KBEntryIn(BaseModel):
    category: Literal["return", "refund", "shipping", "cancellation", "other"]
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=5000)


class ApproveIn(BaseModel):
    # The text the agent wants to send (AI text as-is, or edited)
    final_reply: str = Field(min_length=1, max_length=2000)
