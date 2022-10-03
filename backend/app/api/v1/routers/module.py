from fastapi import APIRouter, Request, Depends, Response, encoders, status, HTTPException
from fastapi_pagination import Page, paginate, LimitOffsetPage
from sqlalchemy import and_

from app.api.dependencies.check_permissions import CheckPermission
from app.db import models, schemas
from app.db.enums import ReturnType
from app.db.session import get_db
from app.db.crud import modules, permissions
from app.core.auth import get_current_user

module_router = mr = APIRouter()

module_check_permission = lambda permission: CheckPermission("modules", permission)


@mr.get(
    "/{module_id}",
    response_model=schemas.ModuleView,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(module_check_permission('view'))]

)
async def module_information_get(
        module_id: int,
        db=Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Single view  Module information
    """
    module_data = await modules.get(db, current_user, id=module_id)
    if current_user.is_superuser:
        return module_data
    for data in current_user.modules:
        if data.id == module_id:
            return module_data
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="module data not found"
    )


@mr.post(
    "",
    response_model=schemas.ModuleDetailView,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(module_check_permission('create'))]

)
async def module_create(
        module: schemas.ModuleCreate,
        db=Depends(get_db),
        current_user=Depends(get_current_user),

):
    """
    Insert a new module information
    """
    return await modules.create(db, current_user, obj_in=module, unique_field=('name',))


@mr.get(
    "",
    response_model=LimitOffsetPage[schemas.ModuleView],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(module_check_permission('list'))]

)
async def module_list(
        request: Request,
        db=Depends(get_db),
        current_user=Depends(get_current_user),

):
    """
    Get all module information
    """
    if current_user.is_superuser:
        return paginate(await modules.get_all(db, current_user, query_params=dict(request.query_params)))
    return paginate(await modules.get_module_list(db, current_user, query_params=dict(request.query_params)))


@mr.put(
    "/{module_id}",
    response_model=schemas.ModuleDetailView,
    response_model_exclude_none=True,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(module_check_permission('edit'))]

)
async def module_information_edit(
        module_id: int,
        module: schemas.ModuleUpdate,
        db=Depends(get_db),
        current_user=Depends(get_current_user),

):
    """
    Update existing module information
    """

    if current_user.is_superuser:
        return await modules.update(db, current_user, id=module_id, obj_in=module, unique_field=("name",))
    for data in current_user.modules:
        if data.id == module_id:
            return await modules.update(db, current_user, id=module_id, obj_in=module, unique_field=("name",))
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="module data not found"
    )


@mr.delete(
    "/{module_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(module_check_permission('delete'))]
)
async def module_delete(
        module_id: int,
        db=Depends(get_db),
        current_user=Depends(get_current_user)

):
    """
    Delete existing module information
    """
    return await modules.remove(db, current_user, id=module_id)


