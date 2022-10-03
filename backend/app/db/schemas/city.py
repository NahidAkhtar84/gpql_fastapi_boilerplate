from pydantic import BaseModel, validator
from fastapi import HTTPException, status
from app.db import enums
from app.db.enums import Status
from . import validate_status
from app.db.schemas.common import (
    CommonBase,
    LiteResponse,
    validate_string_field_check,
    validate_none_check,
    validate_status
)
from app.db.schemas.country import CountryLite


class CityBase(CommonBase):
    description: str = None


class CityUpdate(CityBase):
    code: str
    country_id: int
    status: int = Status.ACTIVE.value

    @validator('status')
    def validate_status(cls, status_field):
        values = [data.value for data in Status]
        if status_field not in values:
            raise ValueError("Invalid status!")
        return status_field

    class Config:
        orm_mode = True


class CityCreate(CityBase):
    code: str
    country_id: int

    class Config:
        orm_mode = True


class CityView(CityBase):
    id: int
    code: str
    status: str
    country: CountryLite

    @validator('status')
    def validate_status_response(cls, status_field):
        return validate_status(status_field)

    class Config:
        orm_mode = True


class CityDetailView(BaseModel):
    detail: str
    data: CityView


class CityLite(CommonBase):
    id: int

    class Config:
        orm_mode = True
