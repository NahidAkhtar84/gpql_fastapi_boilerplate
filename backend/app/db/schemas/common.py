import re
from pydantic import BaseModel, validator

from app.db.enums import Status


def validate_string_field_check(name_field):
    if name_field is not None:
        # name_field = re.sub('[!*)@#%(&$_^]', '', name_field)
        name_field = " ".join(name_field.split())
    if not name_field:
        name_field = None
    if name_field is not None and len(name_field) < 2:
        raise ValueError(f"field length must be greater than 2")
    return name_field


def validate_none_check(name_field):
    if not name_field:
        raise ValueError("Empty value not excepted")
    return name_field


def validate_status(status_field):
    try:
        return Status(int(status_field)).name
    except:
        pass
    return status_field


class CommonBase(BaseModel):
    name: str

    @validator('name')
    def validate_name(cls, name_field):
        return validate_string_field_check(name_field)

    @validator('name')
    def validate_none_name(cls, name_field):
        return validate_none_check(name_field)


class LiteResponse(BaseModel):
    id: int = None
    name: str = None

    class Config:
        orm_mode = True
