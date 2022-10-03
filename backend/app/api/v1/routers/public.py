from typing import List
from sqlalchemy import and_
from sqlalchemy.sql import exists
from fastapi import APIRouter, status, Depends
from fastapi import APIRouter, Request, Depends, Response, encoders, status, HTTPException
from fastapi_pagination import Page, paginate, LimitOffsetPage

from app.core.auth import get_current_user
from app.core.utils import get_all_api_endpoint
from app.db import models, schemas
from app.db.crud import countries
from app.db.crud.status import status_types_get
from app.db.enums import Status, ReturnType
from app.db.session import get_db

public_router = pr = APIRouter()


@pr.get("/status")
async def get_status_types():
    """
    Get all types of status
    """
    return status_types_get()


@pr.get(
    "/country",
    response_model=List[schemas.CountryPublicView],
    status_code=status.HTTP_200_OK
)
async def country_active_list(
        db=Depends(get_db),
):
    """
    Get all active country information
    """
    return await countries.get_data(db, ReturnType.ALL.value, status=Status.ACTIVE.value)


@pr.get(
    "/api_end_point",
    response_model=List[schemas.ApiEndPoint],
    status_code=status.HTTP_200_OK
)
async def get_api_end_point(
        request: Request
):
    """
    Get all api end point
    """
    api_end_point_set, url_method_dict = get_all_api_endpoint(request)
    api_end_point_list = []
    for data in api_end_point_set:
        api_end_point_list.append(
            schemas.ApiEndPoint(
                api_end_point_name=data
            )
        )
    return api_end_point_list


@pr.get(
    "/self_profile"
)
async def user_me(current_user=Depends(get_current_user)):
    """
    Get own information
    """

    return current_user
