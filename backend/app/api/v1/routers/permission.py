from typing import Optional

from fastapi import APIRouter, Request, Depends, status, HTTPException, Header
from fastapi.encoders import jsonable_encoder

from app.api.dependencies.check_permissions import CheckPermission
from app.db import models, schemas
from app.db.enums import ReturnType, Status
from app.db.session import get_db
from app.db.crud import permissions, groups, modules
from app.core.auth import get_current_user

permission_router = pr = APIRouter()


def permission_check_permission(
        permission): return CheckPermission("permissions", permission)


@pr.get(
    "/{module_id}/{group_id}",
    response_model=schemas.PermissionView,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(permission_check_permission('list'))]

)
async def get_permission(
        request: Request,
        module_id: int,
        group_id: int,
        db=Depends(get_db),
        current_user=Depends(get_current_user),
        x_language_code: Optional[str] = Header('en')

):
    """
    get list of permission
    """
    current_user = None
    group_data = await groups.get(db, current_user, group_id)
    module_data = await modules.get(db, current_user, module_id)
    return schemas.PermissionView(
        module=module_data,
        group=group_data,
        menu_permissions=await permissions.get_module_and_group_based_permission(db, request, group_data, module_data)
    )


@pr.post(
    "",
    response_model=schemas.PermissionDetailView,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(permission_check_permission('create'))]

)
async def permission_set(
        request: Request,
        permission_data: schemas.PermissionCreate,
        db=Depends(get_db),
        current_user=Depends(get_current_user),
        x_language_code: Optional[str] = Header('en')
):
    """
    Set a  Permission
    """
    if permission_data.group_id == 1:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Super user get all menu permission. So, can't set menu permission for this user"
        )
    # check module and group id is valid or not
    await groups.get(db, current_user, permission_data.group_id)
    await modules.get(db, current_user, permission_data.module_id)

    await permissions.set_permission(db, request, permission_data)

    # log out of this user group
    user_list = []
    groups_all_user = db.query(models.User).filter(
        models.User.deleted_at == None,
        models.User.status == Status.ACTIVE.value,
        models.User.groups.any(id=permission_data.group_id)
    ).all()
    for user in groups_all_user:
        user.meta = user.version_renew
        user_list.append(user.__dict__)
    db.bulk_update_mappings(models.User, jsonable_encoder(user_list))
    db.commit()
    return schemas.PermissionDetailView(
        detail="Successfully set Permissions"
    )
