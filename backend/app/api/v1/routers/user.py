import jwt
from starlette import status
from typing import Dict, List

from fastapi import APIRouter, Request, Depends, Response, encoders, BackgroundTasks
from fastapi_pagination import Page, paginate, LimitOffsetPage
from typing import Optional

from app.api.dependencies.check_permissions import CheckPermission
from app.core.email import send_email
from app.db.enums import MailSendType
from app.db.schemas import (
    UserEdit,
    UserCreate,
    UserActionResponse,
    UserResponse,
    UserViewResponse,
    PasswordChange,
    UserSignUPBase, UserCreateBase
)
from app.core.auth import (
    sign_up_user, get_current_active_user
)
from app.db.session import get_db
from app.db.models import User
from app.core.auth import authenticate_user
from app.core import security
from app.core.auth import get_current_user
from app.db.crud import (
    edit_user,
    get_users,
    get_user,
    delete_user, edit_user_password,
    new_user_create,
    self_info_update
)


user_router = r = APIRouter()

user_check_permission = lambda permission: CheckPermission("users", permission)


@r.get(
    "",
    response_model=LimitOffsetPage[UserResponse],
    dependencies=[Depends(user_check_permission('list'))]
)
async def users_list(
        request: Request,
        response: Response,
        db=Depends(get_db),
        current_user=Depends(get_current_active_user)
):
    """
    Get all users
    """
    user_list = await get_users(db, current_user, query_params=dict(request.query_params))

    return paginate(user_list)


@r.get(
    "/{user_id}",
    response_model=UserViewResponse,
    dependencies=[Depends(user_check_permission('view'))]
)
async def user_details(
        user_id: int,
        db=Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Get any user details
    """
    user = await get_user(db, current_user, user_id)
    return user


@r.post("")
async def add_new_user(
        new_user: UserCreateBase,
        background_tasks: BackgroundTasks,
        db=Depends(get_db),
        current_user=Depends(get_current_active_user)
):
    db_new_user, password = await new_user_create(db, current_user, new_user)
    try:
        background_tasks.add_task(
            send_email,
            email=new_user.email,
            type=MailSendType.NEW_USER_SEND_PASSWORD.value,
            data=db_new_user,
            password=password
        )
    except:
        logger.error("Something went wrong", exc_info=1)
    return {"detail": "Successfully created a new user"}


@r.put(
    "/{user_id}",
    response_model_exclude_none=True,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(user_check_permission('edit'))]
)
async def user_edit(
        user_id: int,
        user: UserEdit,
        db=Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Update user
    """
    user_data = await edit_user(db, current_user, user_id, user)
    return {"detail": "Successfully updated user information"}


@r.put(
    "/self_update",
    response_model_exclude_none=True,
    status_code=status.HTTP_202_ACCEPTED,
)
async def user_edit(
        user: UserEdit,
        db=Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Update user
    """
    user_data = await self_info_update(db, current_user, current_user.id, user)
    return {"detail": "Successfully updated user information"}


@r.patch(
    "/password_change",
    response_model_exclude_none=True,

)
async def user_password_edit(
        request: Request,
        user_password_update: PasswordChange,
        db=Depends(get_db),
        current_user=Depends(get_current_user),
):
    """
    Changed  user password
    """
    user = await edit_user_password(db, current_user, user_password_update)
    return "Successfully changed password"


@r.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(user_check_permission('delete'))]
)
async def user_delete(
        user_id: int,
        db=Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Delete existing user
    """
    await delete_user(db, current_user, user_id)
    return {"detail": "Successfully deleted user data"}


@r.get(
    "/log_out",
    status_code=status.HTTP_200_OK,
)
async def log_out_all_device(
        db=Depends(get_db),
        current_user=Depends(get_current_user),
):
    """
    log out all device by a user
    """
    current_user.meta = current_user.version_renew
    db.add(current_user)
    db.commit()
    return {"detail": "Successfully logged out from all devices"}
