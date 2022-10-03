from typing import Text

from pydantic import BaseModel, validator, EmailStr
from fastapi import HTTPException, status
from app.db import enums
from app.db.enums import Status


class TokenData(BaseModel):
    email: str = None,
    organization_id: int = None


class RefreshTokenPayload(BaseModel):
    email: EmailStr
    token_type: str
