from typing import TypeVar

from fastapi import status, HTTPException

from app.db import models, schemas
from . import modules
from .base import BasicCrud
from ..enums import MenuType, ReturnType
from ..session import Base

ModelType = TypeVar("ModelType", bound=Base)


class MenuCRUD(BasicCrud[models.Menu, schemas.MenuCreate, schemas.MenuUpdate]):
    async def find_root_parent(self, db, parent_id):
        menu_data = await self.get_data(db, ReturnType.SINGLE.value, id=parent_id)
        if menu_data.menu_type == MenuType.PARENT.value:
            return parent_id
        return await self.find_root_parent(db, menu_data.parent_menu)

    async def check_data_validation(self, db, menu_data):
        module = await modules.get_data(db, ReturnType.SINGLE.value, id=menu_data.module_id)
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="module data not found"
            )

        if menu_data.menu_type == MenuType.CHILD.value:
            if menu_data.parent_menu:
                parent = await self.get_data(db, ReturnType.SINGLE.value, id=menu_data.parent_menu)
                if not parent:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="parent data not found"
                    )
                if parent.module_id != menu_data.module_id:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Parent and child module are not same"
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Parent filed missing. Please insert parent data"
                )
        return True


menus = MenuCRUD(models.Menu)
