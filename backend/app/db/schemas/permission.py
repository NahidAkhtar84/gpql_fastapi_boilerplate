from typing import  List

from pydantic import BaseModel
from app.db.enums import Status
from app.db.schemas import GroupLite, ModuleLite


class PermissionOperation(BaseModel):
    create: bool = None
    edit: bool = None
    view: bool = None
    list: bool = None
    delete: bool = None


class PermissionBase(PermissionOperation):
    menu_id: int


class PermissionCreate(BaseModel):
    module_id: int
    group_id: int
    menu_permission: List[PermissionBase]

    class Config:
        orm_mode = True


class PermissionMenuView(PermissionOperation):
    id: int
    menu_name: str

    class Config:
        orm_mode = True


class PermissionView(BaseModel):
    module: ModuleLite
    group: GroupLite
    menu_permissions: List[PermissionMenuView] = None


class PermissionModuleView(BaseModel):
    id: int
    module_name: str
    menu_permissions: List[PermissionMenuView] = None

    class Config:
        orm_mode = True


class PermissionListView(BaseModel):
    group: GroupLite
    permissions: List[PermissionModuleView]

    class Config:
        orm_mode = True


class PermissionDetailView(BaseModel):
    detail: str


class PermissionScriptBase(PermissionBase):
    group_id: int
    module_id: int
    status:int = Status.ACTIVE.value

    class Config:
        orm_mode = True
