from pydantic import BaseModel
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
    user_id: str
    name: str
    segment: str
    created_at: datetime
    last_seen_at: datetime

    class Config:
        from_attributes = True


class MessageOut(BaseModel):
    user_message: str
    assistant_reply: str
    intent: str
    needs_human_support: bool
    created_at: datetime

    class Config:
        from_attributes = True
