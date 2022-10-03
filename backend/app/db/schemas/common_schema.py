from typing import Text

from pydantic import BaseModel, validator
from fastapi import HTTPException, status
from app.db import enums
from app.db.enums import Status
from app.db.schemas.common import (
    CommonBase,
    LiteResponse,
    validate_string_field_check,
    validate_none_check,
    validate_status
)


class BaseSchema(CommonBase):
    description: Text = None


class UpdateSchema(BaseSchema):
    status: int = Status.ACTIVE.value

    @validator('status')
    def validate_status(cls, status_field):
        values = [data.value for data in Status]
        if status_field not in values:
            raise ValueError("Invalid status!")
        return status_field

    class Config:
        orm_mode = True


class BaseResponseSchema(BaseModel):
    name: str
    description: Text = None
    status: str

    @validator('status')
    def validate_status_response(cls, status_field):
        return validate_status(status_field)


class CreateSchema(BaseSchema):
    class Config:
        orm_mode = True


class ViewSchema(BaseResponseSchema):
    id: int

    class Config:
        orm_mode = True


class DetailViewSchema(BaseModel):
    detail: str
    data: ViewSchema
