from fastapi import APIRouter, Request, Depends, Response, encoders, status, HTTPException
from fastapi_pagination import Page, paginate, LimitOffsetPage

from app.api.dependencies.check_permissions import CheckPermission
from app.db import models, schemas
from app.db.session import get_db
from app.db.crud import groups
from app.core.auth import get_current_user

group_router = gr = APIRouter()

group_check_permission = lambda permission: CheckPermission("groups", permission)


@gr.get(
    "/{group_id}",
    response_model=schemas.GroupView,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(group_check_permission('view'))]

)
async def group_information_get(
        group_id: int,
        db=Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Single view  group information
    """
    return await groups.get(db, current_user, id=group_id)


@gr.post(
    "",
    response_model=schemas.GroupDetailView,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(group_check_permission('create'))]

)
async def group_create(
        group: schemas.GroupCreate,
        db=Depends(get_db),
        current_user=Depends(get_current_user)

):
    """
    Insert a new group information
    """
    return await groups.create(db, current_user, obj_in=group, unique_field=('name',))


@gr.get(
    "",
    response_model=LimitOffsetPage[schemas.GroupView],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(group_check_permission('list'))]

)
async def group_list(
        request: Request,
        db=Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Get all group information
    """
    return paginate(await groups.get_all(db, current_user, query_params=dict(request.query_params)))


@gr.put(
    "/{group_id}",
    response_model=schemas.GroupDetailView,
    response_model_exclude_none=True,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(group_check_permission('edit'))]

)
async def group_information_edit(
        group_id: int,
        group: schemas.GroupUpdate,
        db=Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Update existing group information
    """
    return await groups.update(db, current_user, id=group_id, obj_in=group, unique_field=("name",))


@gr.delete(
    "/{group_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(group_check_permission('delete'))]
)
async def module_delete(
        group_id: int,
        db=Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Delete existing module information
    """
    return await groups.remove(db, current_user, id=group_id)
