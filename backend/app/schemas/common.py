from __future__ import annotations
import uuid
from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class IdResponse(BaseModel):
    id: uuid.UUID
