import shutil
import os
import uuid

from fastapi import APIRouter, Request, FastAPI, File, Header, Depends, UploadFile, HTTPException
from starlette import status

from app.core.auth import get_current_user, image_upload_size_check
from app.core.const import COUNTRY_FILE_UPLOAD_PATH
from app.core.utils import file_upload
from app.db import schemas
from app.db.crud import countries
from app.db.enums import ReturnType
from app.db.session import get_db
from app.api.dependencies.check_permissions import CheckPermission

files_router = r = APIRouter()

ALLOWED_FILE_EXTENSIONS = ['jpg', 'jpeg', 'png']

countries_logo_upload_check_permission = lambda permission: CheckPermission("files_countries_logo_uploads", permission)


@r.put(
    "/countries_logo_uploads/{country_id}",
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(image_upload_size_check),
        Depends(countries_logo_upload_check_permission('edit'))
    ]
)
async def country_logo_upload(
        country_id: int,
        file: UploadFile = File(...),
        db=Depends(get_db),
        current_user=Depends(get_current_user),
):
    country_data = await countries.get_data(db, ReturnType.SINGLE.value, id=country_id)
    if not country_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="country not found")
    file_location = file_upload(file, COUNTRY_FILE_UPLOAD_PATH)
    country_data.logo = file_location
    db.add(country_data)
    db.commit()
    return "Successfully uploaded country logo"
