from __future__ import annotations
import uuid
from dataclasses import dataclass
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.utils.tokens import decode_access_token

security = HTTPBearer(auto_error=False)


@dataclass
class CurrentUser:
    id: uuid.UUID
    role: str


async def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> CurrentUser:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_access_token(credentials.credentials)
        return CurrentUser(id=uuid.UUID(payload["sub"]), role=payload.get("role", "buyer"))
    except (jwt.PyJWTError, ValueError, KeyError) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from e


async def get_optional_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> CurrentUser | None:
    if credentials is None:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        return CurrentUser(id=uuid.UUID(payload["sub"]), role=payload.get("role", "buyer"))
    except (jwt.PyJWTError, ValueError, KeyError):
        return None


def require_role(*roles: str):
    async def checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user
    return checker


require_buyer = require_role("buyer", "seller", "admin", "superadmin")
require_seller = require_role("seller", "admin", "superadmin")
require_admin = require_role("admin", "superadmin")
require_superadmin = require_role("superadmin")
