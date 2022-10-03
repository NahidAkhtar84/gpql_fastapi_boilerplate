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


class CountryBase(CommonBase):
    code: str
    currency_name: str
    currency_code: str
    currency_number: int
    description: str = None


class CountryUpdate(CountryBase):
    status: int = Status.ACTIVE.value

    @validator('status')
    def validate_status(cls, status_field):
        values = [data.value for data in Status]
        if status_field not in values:
            raise ValueError("Invalid status!")
        return status_field

    class Config:
        orm_mode = True


class CountryCreate(CountryBase):
    class Config:
        orm_mode = True


class CountryView(CountryBase):
    id: int
    status: str
    logo: Text = None

    @validator('status')
    def validate_status_response(cls, status_field):
        return validate_status(status_field)

    class Config:
        orm_mode = True


class CountryDetailView(BaseModel):
    detail: str
    data: CountryView


class CountryModeLite(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class CountryLite(CommonBase):
    id: int
    code: str
    logo: Text = None

    class Config:
        orm_mode = True


class CountryPublicView(CommonBase):
    id: int
    logo: Text = None

    class Config:
        orm_mode = True
