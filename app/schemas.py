from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List


class MessageRequest(BaseModel):
    user_id: str
    name: str
    message: str


class MessageResponse(BaseModel):
    reply: str
    intent: str
    user_segment: str
    needs_human_support: bool


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    name: str
    segment: str
    created_at: datetime
    last_seen_at: datetime


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_message: str
    assistant_reply: str
    intent: str
    needs_human_support: bool
    created_at: datetime
