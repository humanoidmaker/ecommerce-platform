from __future__ import annotations
import uuid
from datetime import datetime
from pydantic import BaseModel


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    phone: str | None = None
    avatar_url: str | None = None
    role: str
    is_active: bool
    email_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
