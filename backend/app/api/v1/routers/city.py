from fastapi import APIRouter, Request, Depends, Response, encoders, status, HTTPException
from fastapi_pagination import Page, paginate, LimitOffsetPage

from app.api.dependencies.check_permissions import CheckPermission
from app.db import models, schemas
from app.db.session import get_db
from app.db.crud.city import cities
from app.core.auth import get_current_user
from app.db.crud.user import data_validation_check

city_router = cr = APIRouter()

city_check_permission = lambda permission: CheckPermission("city", permission)


@cr.get(
    "/{city_id}",
    response_model=schemas.CityView,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(city_check_permission('view'))]

)
async def city_get(
        city_id: int,
        db=Depends(get_db),
        current_user=Depends(get_current_user)

):
    """
    Single view  City information
    """

    return await cities.get(db, current_user, city_id)


@cr.post(
    "",
    response_model=schemas.CityDetailView,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(city_check_permission('create'))]

)
async def city_create(
        city: schemas.CityCreate,
        db=Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Create a new City
    """
    validation_data = [
        (models.Country, city.country_id)
    ]
    await data_validation_check(db, validation_data)

    city_data = await cities.create(db, current_user, obj_in=city, unique_field=('name', 'code', 'country_id'))
    return city_data


@cr.get(
    "",
    response_model=LimitOffsetPage[schemas.ViewSchema],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(city_check_permission('list'))]

)
async def city_list(
        request: Request,
        db=Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Get all cities
    """
    return paginate(await cities.get_all(db, current_user, query_params=dict(request.query_params)))


@cr.put(
    "/{city_id}",
    response_model=schemas.CityDetailView,
    response_model_exclude_none=True,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(city_check_permission('edit'))]

)
async def city_edit(
        city_id: int,
        city: schemas.CityUpdate,
        db=Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Update existing City
    """
    if city.country_id:
        validation_data = [
            (models.Country, city.country_id)
        ]
        await data_validation_check(db, validation_data)

    city_data = await cities.update(
        db, current_user, id=city_id, obj_in=city,
        unique_field=("name", "code", "country_id")
    )
    return city_data


@cr.delete(
    "/{city_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(city_check_permission('delete'))]

)
async def city_delete(
        city_id: int,
        db=Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Delete existing city
    """
    await cities.remove(db, current_user, id=city_id)
    return {"detail": "Successfully deleted city data"}
