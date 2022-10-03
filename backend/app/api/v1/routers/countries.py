from fastapi import APIRouter, Request, Depends, Response, encoders, status, HTTPException
from fastapi_pagination import Page, paginate, LimitOffsetPage

from app.api.dependencies.check_permissions import CheckPermission
from app.db import models, schemas
from app.db.enums import Status, ReturnType
from app.db.session import get_db
from app.db.crud import countries
from app.core.auth import get_current_user
from app.core.log_config import log_config

logger = log_config()


country_router = cr = APIRouter()

country_check_permission = lambda permission: CheckPermission("countries", permission)


@cr.get(
    "/{country_id}",
    response_model=schemas.CountryView,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(country_check_permission('view'))]

)
async def country_information_get(
        country_id: int,
        db=Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Single view  Country information
    """
    return await countries.get(db, current_user, id=country_id)


@cr.post(
    "",
    response_model=schemas.CountryDetailView,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(country_check_permission('create'))]

)
async def country_create(
        country: schemas.CountryCreate,
        db=Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Insert a new country information
    """
    return await countries.create(db, current_user, obj_in=country, unique_field=('name', 'code'))


@cr.get(
    "",
    response_model=LimitOffsetPage[schemas.CountryView],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(country_check_permission('list'))]

)
async def country_list(
        request: Request,
        db=Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Get all country information
    """
    return paginate(await countries.get_all(db, current_user, query_params=dict(request.query_params)))


@cr.put(
    "/{country_id}",
    response_model=schemas.CountryDetailView,
    response_model_exclude_none=True,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(country_check_permission('edit'))]

)
async def country_information_edit(
        country_id: int,
        country: schemas.CountryUpdate,
        db=Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Update existing country information
    """
    return await countries.update(db, current_user, id=country_id, obj_in=country, unique_field=("name", "code"))


@cr.delete(
    "/{country_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(country_check_permission('delete'))]
)
async def country_delete(
        country_id: int,
        db=Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Delete existing country information
    """
    return await countries.remove(db, current_user, id=country_id)
