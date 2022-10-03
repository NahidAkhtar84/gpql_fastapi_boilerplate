import jwt

from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks, Header
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional

from app.core.email import send_email
from app.db import enums, models
from app.db.enums import MailSendType, ReturnType, Status
from app.core.utils import verify_token_by_get_id
from app.db.crud import permissions, get_user, modules, get_model
from app.db.schemas import (
    UserSignUPBase,
    UserLogin,
    LoginResponse,
    SignupResponse,
    RefreshToken, ForgetPassword, ResetPassword
)
from app.core.auth import (
    sign_up_user,
    get_user_by_email,
    get_domain_org_info, get_user_by_email_is_superuser
)
from app.db.session import get_db
from app.db.models import User
from app.core.auth import authenticate_user
from app.core import security
from app.core.log_config import log_config

logger = log_config()

auth_router = r = APIRouter()


@r.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
        request: Request,
        user: UserSignUPBase,
        background_tasks: BackgroundTasks,
        db=Depends(get_db),
        x_org_domain: Optional[str] = Header(None)
):
    user.email = user.email.lower()
    organization = get_domain_org_info(request, db)

    db_user_org = await sign_up_user(db, user, organization.id)
    try:
        background_tasks.add_task(
            send_email,
            request=request,
            email=user.email,
            id=db_user_org.id,
            type=enums.MailSendType.VERIFICATION.value
        )
    except:
        logger.error("Something went wrong. Mail does not send", exc_info=1)
    return {"detail": "Please check email to verify your account!"}


@r.post("/resend-email/{email}")
async def resend_verification_email(
        request: Request,
        email: str,
        background_tasks: BackgroundTasks,
        db=Depends(get_db),
        x_org_domain: Optional[str] = Header(None)
):
    organization = get_domain_org_info(request, db)
    db_user_org = get_model(
        db,
        models.User,
        organization_id=organization.id,
        email=email
    )
    if not db_user_org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user found with this email to  resend verification link!"
        )
    if db_user_org.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already verified!"
        )
    try:
        background_tasks.add_task(
            send_email,
            email=email.lower(),
            id=db_user_org.id,
            type=enums.MailSendType.VERIFICATION.value
        )
    except:
        logger.error("Something went wrong", exc_info=1)
    return {"detail": "Please check email to verify your account!"}


@r.get('/verification/{token}', status_code=status.HTTP_201_CREATED)
async def sign_up_verification(
        request: Request,
        token: str,
        db=Depends(get_db),
        x_org_domain: Optional[str] = Header(None)
):
    user_org_id = verify_token_by_get_id(token)
    organization = get_domain_org_info(request, db)
    db_user_organization = await get_model(db, models.User, id=user_org_id, organization_id=organization.id)
    if not db_user_organization or db_user_organization.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Verification token invalid or expired"
        )
    db_user_organization.status = enums.Status.ACTIVE.value
    db_user_organization.meta = db_user_organization.version_renew
    db.add(db_user_organization)
    db.add(db_user_organization)
    db.commit()

    return {"detail": "Account has been verified successfully"}


@r.post("/token")
async def token(
        db=Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends(),

):
    user = await authenticate_user(db, form_data.username, form_data.password, 1)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, exp = await security.create_access_token(user=user)
    return {"access_token": access_token, "token_type": "bearer"}


@r.post("/login")
async def login(
        request: Request,
        user_login_info: UserLogin,
        db=Depends(get_db)
):
    user = get_user_by_email_is_superuser(db, user_login_info.email)
    if not user:
        organization = get_domain_org_info(request, db)
        user: models.User = await authenticate_user(
            db, user_login_info.email.lower(),
            user_login_info.password,
            organization_id=organization.id
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account activation required",
            )
    else:
        domain = request.headers.get('x-org-domain')
        organization = None
        if domain:
            organization = get_domain_org_info(request, db)
    domain = organization.domain if organization else None
    access_token, exp = await security.create_access_token(domain, user)
    refresh_token = await security.create_refresh_token(domain, user)
    menu_permissions = await permissions.get_permissions_by_user_login(db, request, user)
    response_data = LoginResponse(
        email=user.email,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        permissions=menu_permissions,
        expiry_time=exp,
        username=user.username,
        phone=user.phone
    )
    return response_data


@r.post("/refresh-token")
async def refresh_token(
        request: Request,
        refreash: RefreshToken, db=Depends(get_db)

):
    ref_token = refreash.refresh_token
    try:
        token_user = security.get_access_from_refresh_token(db, refresh_token=ref_token)
    except jwt.exceptions.ExpiredSignatureError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
    login_token = await security.create_login_token(user=token_user, refresh_token=ref_token)

    menu_permissions = await permissions.get_permissions_by_user_login(db, request, token_user)

    response_data = LoginResponse(
        email=token_user.email,
        username=token_user.username,
        access_token=login_token['access_token'],
        refresh_token=login_token['refresh_token'],
        token_type="bearer",
        phone=token_user.phone,
        full_name=token_user.full_name,
        menu_permissions=menu_permissions,
        expiry_time=login_token['expiry_time']
    )
    return response_data


@r.post('/forget_password', status_code=status.HTTP_201_CREATED)
async def forget_password(
        request: Request,
        forget_password: ForgetPassword,
        background_tasks: BackgroundTasks,
        db=Depends(get_db)
):
    db_user = get_user_by_email(db, forget_password.email)

    if db_user:
        try:
            db_user.meta = dict(db_user.meta)
        except:
            db_user.meta = {}
        db_user.meta['password_reset'] = "On_going"
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        try:
            background_tasks.add_task(
                send_email, email=db_user.email,
                id=db_user.id, type=MailSendType.VERIFICATION.value)
        except:
            return {"detail": "Something went wrong! Please try again"}

        return {"detail": "Please check your email to reset password"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No user exist in this email"
    )


@r.patch('/reset_password/{token}', status_code=status.HTTP_201_CREATED)
async def reset_password(
        token: str,
        reset_password: ResetPassword,
        db=Depends(get_db)
):
    user_id = verify_token_by_get_id(token)
    db_user = await get_user(db, user_id)

    if db_user.meta['password_reset'] == "On_going":
        update_data = reset_password.dict(exclude_unset=True)
        hashed_password = security.get_password_hash(update_data["new_password"])
        if update_data["new_password"] != update_data["confirm_password"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="New password and confirm password are not same!")
        else:
            data = {
                "password": hashed_password
            }

            for key, value in data.items():
                setattr(db_user, key, value)
            db_user.meta = db_user.version_renew
            db_user.meta['password_reset'] = "Done"
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return {"detail": "Password successfully reset"}
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Token is expired"
        )
