import jwt
from typing import Optional
from sqlalchemy.orm.session import Session
from fastapi import Depends, HTTPException, status, Request, Header
from .const import GROUP_LIST, IMAGE_UPLOAD_MAX_SIZE, VIDEO_UPLOAD_MAX_SIZE

from app.core import security
from app.db import models, schemas, session
from app.db.enums import Status
from app.db.models import organization
from .const import GROUP_LIST
from app.core.log_config import log_config

logger = log_config()


def get_domain_org_info(
        request: Request, db: Session
):
    domain = request.headers.get('x-org-domain')
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="x-org-domain must be specified in request headers"
        )
    db_organization = db.query(models.Organization).filter(models.Organization.domain == domain).first()
    if not db_organization or db_organization.status != Status.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization not found with the domain: {domain}!"
        )
    return db_organization


async def get_current_user(
        request: Request,
        db=Depends(session.get_db), token: str = Depends(security.oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, security.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        email: str = payload.get("email")
        domain: str = payload.get("domain")
        if not email:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    super_user = get_user_by_email(db, email, organization_id=None)
    if super_user:
        return super_user
    db_organization = get_domain_org_info(request, db)
    if db_organization.domain != domain:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Organization miss-matched with x-org-domain and token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_user_by_email(db, email, organization_id=db_organization.id)
    if not user or not user.is_active:
        raise credentials_exception
    version = user.meta.get('version', None) if user.meta else None
    if not version == payload.get('version'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    return user


async def get_current_active_user(
        request: Request,
        current_user: models.User = Depends(get_current_user),
        db=Depends(session.get_db)
):
    if current_user.is_superuser:
        try:
            db_organization = get_domain_org_info(request, db)
            current_user.organization_id = db_organization.id
            current_user.organization = db_organization
        except:
            logger.error("x-org-domain not found request headers")
    return current_user


async def get_current_admin_or_superadmin(
        current_user=Depends(get_current_user)
):
    if current_user.is_superuser or current_user.is_admin:
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this resource"
    )


async def get_current_agent(
        current_user=Depends(get_current_user)
):
    if current_user.is_agent:
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this resource"
    )


async def sign_up_user(db: Session, user: schemas.UserSignUPBase, organization_id) -> models.User:
    hashed_password = security.get_password_hash(user.password)
    if get_user_by_email(db, user.email, organization_id):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="User with this email address already exists",
        )
    # customer group id will always be # and name="Customer"
    group = get_or_create(db, models.Group, name=GROUP_LIST[3], status=1, is_protected=True)
    # Organization with this name will be created with script before launch
    # organization = get_or_create(db, models.Organization, name="Hidmona")

    validation_data = [
        (models.Country, user.country_id),
        (models.City, user.city_id)
    ]
    # imported here cz having circular deped errror
    from app.db.crud.user import data_validation_check
    # default module for customer will be Customer Management

    if user.is_citizen == False:
        citizen_country_id = user.citizen_country_id
        validation_data.append((models.Country, citizen_country_id))
    else:
        citizen_country_id = None

    await data_validation_check(db, validation_data)
    from app.db.crud.utils import phone_number_validation_check
    phone_number_validation_check(db, user)

    async def sign_up_user(db: Session, user: schemas.UserSignUPBase) -> models.User:
        hashed_password = security.get_password_hash(user.password)
        if get_user_by_email(db, user.email):
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail="User with this email address already exists",
            )
        # customer group id will always be # and name="Customer"
        group = get_or_create(db, models.Group, name=GROUP_LIST[3], status=1, is_protected=True)

        validation_data = [
            (models.Country, user.country_id),
            (models.City, user.city_id)
        ]
        # imported here cz having circular deped errror
        from app.db.crud.user import data_validation_check

        if user.is_citizen == False:
            citizen_country_id = user.citizen_country_id
            validation_data.append((models.Country, citizen_country_id))
        else:
            citizen_country_id = None

        await data_validation_check(db, validation_data)
        from app.db.crud.utils import phone_number_validation_check
        phone_number_validation_check(db, user)

        db_user = models.User(
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            password=hashed_password,
            phone=user.phone,
            organization_id=organization_id,
            country_id=user.country_id,
            city_id=user.city_id,
            is_citizen=user.is_citizen,
            citizen_country_id=citizen_country_id,
            date_of_birth=user.date_of_birth,
            street_address=user.street_address,
            postal_code=user.postal_code,
            is_active=False
        )
        db_user.groups.append(group)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    db_user.groups.append(group)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


async def authenticate_user(db, email: str, password: str, organization_id: int):
    user = get_user_by_email(db, email, organization_id)
    if not user:
        return False
    if not security.verify_password(password, user.password):
        return False
    return user


# def get_user_by_email(db: Session, email: str) -> schemas.UserSignUPBase:
#     return db.query(models.User).filter(
#         models.User.email == email, models.User.deleted_at == None).first()

def get_user_by_email(db: Session, email: str, organization_id) -> schemas.UserSignUPBase:
    print(email, organization_id)
    return db.query(models.User).filter(
        models.User.email == email,
        models.User.deleted_at == None,
        models.User.organization_id == organization_id
    ).first()


def get_user_by_email_is_superuser(db, email):
    return db.query(models.User).filter(
        models.User.email == email,
        models.User.deleted_at == None,
        models.User.groups.any(id=1)
    ).first()


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


def get_domain_org_info(
        request: Request, db: Session
):
    domain = request.headers.get('x-org-domain')
    print(domain)
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="x-org-domain must be specified in request headers"
        )
    organization = db.query(models.Organization).filter(models.Organization.domain == domain).first()
    if not organization or organization.status != Status.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization not found with the domain: {domain}!"
        )
    return organization


async def get_domain_org(
        request: Request,
        db=Depends(session.get_db)
):
    return get_domain_org_info(request, db)

async def image_upload_size_check(
        content_length: Optional[int] = Header(None, lt=IMAGE_UPLOAD_MAX_SIZE)
):
    return content_length


async def video_upload_size_check(
        content_length: Optional[int] = Header(None, lt=VIDEO_UPLOAD_MAX_SIZE)
):
    return content_length