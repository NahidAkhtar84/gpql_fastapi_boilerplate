from typing import Text, List

from pydantic import BaseModel, validator
from app.db.enums import Status, MenuType
from app.db.schemas import ModuleLite
from app.db.schemas.common import (
    CommonBase,
    LiteResponse,
    validate_string_field_check,
    validate_none_check,
    validate_status
)


class MenuBase(BaseModel):
    name: str
    menu_type: int = MenuType.PARENT.value
    module_id: int
    api_end_point: str = None
    menu_serial: int = None
    menu_icon: str = None
    description: str = None
    menu_url: str = None
    parent_menu: int = None

    @validator('name', 'description')
    def validate_string_variable(cls, name_field):
        return validate_string_field_check(name_field)

    @validator('name')
    def validate_none_string_check(cls, name_field):
        return validate_none_check(name_field)


class MenuCreate(MenuBase):
    class Config:
        orm_mode = True


class MenuUpdate(MenuBase):
    status: int = Status.ACTIVE.value

    @validator('status')
    def validate_status(cls, status_field):
        values = [data.value for data in Status]
        if status_field not in values:
            raise ValueError("Invalid status!")
        return status_field

    class Config:
        orm_mode = True


class ParentLite(BaseModel):
    id: int = None
    name: str = None
    menu_url: str = None

    class Config:
        orm_mode = True


class MenuView(BaseModel):
    name: str
    menu_type: int = MenuType.PARENT.value
    module_id: int
    api_end_point: str = None
    menu_serial: int = None
    menu_icon: str = None
    description: str = None
    menu_url: str = None
    id: int
    status: str
    menu_type_name: str = None
    module: LiteResponse = None
    parent_info: ParentLite = None

    # module: ModuleLite
    @validator('status')
    def validate_status_response(cls, status_field):
        return validate_status(status_field)

    class Config:
        orm_mode = True


class MenuDetailView(BaseModel):
    detail: str
    data: MenuView


class MenuLite(BaseModel):
    id: int
    name: str
    parent_menu: int = None

    class Config:
        orm_mode = True


class ApiEndPoint(BaseModel):
    api_end_point_name: str

    class Config:
        orm_mode = True
