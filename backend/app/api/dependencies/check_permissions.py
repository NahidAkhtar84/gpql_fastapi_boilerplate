from fastapi import status, Depends, HTTPException
from sqlalchemy import or_

from app.db import models, schemas
from app.core.auth import get_current_user
from app.db.crud import permissions, menus
from app.db.enums import ReturnType
from app.db.session import get_db


class CheckPermission:
    def __init__(self, api_end_point: str, permission: str):
        self.api_end_point = api_end_point
        self.permission = permission

    async def __call__(self, user: models.User = Depends(get_current_user), db=Depends(get_db)):
        if user.is_superuser:
            return True
        menu_data = await menus.get_data(
            db, ReturnType.SINGLE.value,
            api_end_point=f"{self.api_end_point}"
        )
        if not menu_data:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted")
        db_permission = db.query(models.Permission).filter(
            or_(
                models.Permission.create == True,
                models.Permission.edit == True,
                models.Permission.view == True,
                models.Permission.list == True,
                models.Permission.delete == True
            ),
            models.Permission.menu_id == menu_data.id,
            models.Permission.group_id.in_(user.group_id_list)
        )
        for data_permission in db_permission:
            permission_operation = schemas.PermissionOperation(**data_permission.__dict__).dict()
            if permission_operation.get(self.permission, None):
                return True
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted")
