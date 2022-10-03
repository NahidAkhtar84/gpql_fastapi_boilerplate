import string, random, pytz, datetime
from typing import Dict, List
from sqlalchemy.orm import Session
from fastapi import status, HTTPException
from fastapi.encoders import jsonable_encoder

from app.core.auth import get_user_by_email, get_user_by_email_is_superuser
from app.core.security import get_password_hash, verify_password
from app.db import schemas, models
from app.core import security, auth
from app.db.crud import groups, countries
from app.db.enums import Status
from app.core.const import GROUP_LIST
from app.db.crud.utils import phone_number_validation_check, search_with_params
from app.db.models.common_base import current_time


async def get_users(
        db: Session, current_user, query_params: Dict = {}
) -> List[schemas.UserResponse]:
    search = query_params.get('search')

    queryset = db.query(models.User).filter(models.User.deleted_at == None)
    print(current_user.__dict__)
    if current_user.organization_id:
        queryset = queryset.filter(models.User.organization_id == current_user.organization_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Auth credentials missing!")

    if search:
        queryset = search_with_params(queryset, search, models.User)

    return queryset.order_by("created_at").all()


async def get_user(
        db: Session, current_user, user_id
) -> schemas.UserViewResponse:
    queryset = db.query(models.User).filter(
        models.User.deleted_at == None, models.User.id == user_id).first()

    if current_user:
        if current_user.is_superuser:
            queryset = queryset
        else:
            queryset = queryset.filter(models.User.created_by_id == current_user.id)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Auth credentials missing!")

    if not queryset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return queryset


async def edit_user_password(
        db: Session, user_password_update: schemas.PasswordChange, current_user
):
    update_data = user_password_update.dict(exclude_unset=True)

    db_user = db.query(models.User).filter(models.User.id == current_user.id).first()

    hashed_password = get_password_hash(update_data["new_password"])

    if update_data["new_password"] != update_data["confirm_password"]:
        # logger.error("New password and confirm password are not same!",exc_info=1)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="New Password and Confirm Password are not same!")
    if not verify_password(update_data["previous_password"], db_user.password):
        # logger.error("Incorrect previous password!",exc_info=1)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect previous password!")

    else:
        data = {
            "password": hashed_password
        }

        for key, value in data.items():
            setattr(db_user, key, value)
        db_user.meta = db_user.version_renew

        db_user.updated_by_id = current_user.id if current_user else None
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user


async def edit_user(
        db: Session, current_user, user_id: int, user: schemas.UserEdit
) -> schemas.UserActionResponse:
    update_data = user.dict(exclude_unset=True)
    user_group_list = []
    if "user_group" in update_data:
        for _group in update_data["user_group"]:
            group = db.query(models.Group).filter(models.Group.id == _group).first()
            if group:
                user_group_list.append(group)
            # if one of the groups are not in db, it will return below error message,
            else:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND,
                    detail="User Group does not exist!"
                )
    db_user = await self_info_update(db, current_user, user_id, user)
    db_user.groups = user_group_list
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


async def self_info_update(
        db: Session, current_user: models.User, user_id, user: schemas.UserSelfUpdate
) -> models.User:
    db_user = await get_user(db, current_user, user_id)
    update_data = user.dict(exclude_unset=True)
    if 'phone' in update_data:
        if update_data['phone'] != db_user.phone:
            update_data['phone'] = phone_number_validation_check(db, user)
    validation_data = [
        (models.Country, user.country_id),
        (models.City, user.city_id)
    ]
    await data_validation_check(db, validation_data)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db_user.updated_by_id = current_user.id if current_user else None
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


async def delete_user(db: Session, current_user, user_id: int):
    try:
        user = await get_user(db, current_user, user_id)
        user.deleted_at = datetime.datetime.now(tz=pytz.timezone('UTC'))
        db.add(user)
        db.commit()
        db.refresh(user)

    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=" Something went wrong")


async def data_validation_check(db: Session, items, **kwargs):
    for item in items:
        # item[0]=Model, item[1]=id
        query = None
        if item[1] != None:
            query = db.query(item[0]).filter(
                item[0].id == item[1],
                item[0].status == Status.ACTIVE.value,
                item[0].deleted_at == None
            ).first()

            if not query:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Selected {item[0].__name__} does not exist!"
                )
    return True


def generate_password():
    total_char = string.ascii_uppercase + string.ascii_lowercase + "0123456789"
    password = [total_char[random.randint(0, len(total_char) - 1)] for _ in range(8)]
    return str("".join(password))


async def insert_new_user(db, current_user, new_user: schemas.UserCreateBase):
    password = generate_password()
    hashed_password = security.get_password_hash(password)
    phone = phone_number_validation_check(db, new_user)
    user_groups = db.query(models.Group).filter(
        models.Group.id.in_(new_user.user_group)
    ).all()
    db_user = models.User(
        is_active=True,
        email=new_user.email,
        country_id=new_user.country_id,
        created_by_id=current_user.created_by_id,
        organization_id=current_user.organization_id,
        username=new_user.user_name,
        password=hashed_password,
        phone=phone,
        groups=user_groups
    )
    db.add(db_user)
    print("password: ", password)
    db.commit()
    return db_user, password


async def new_user_create(db, current_user, new_user: schemas.UserCreateBase):
    email = new_user.email
    for group in new_user.user_group:
        user_group = db.query(models.Group).filter(models.Group.id == group).first()
        if not user_group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User group not found")

    if get_user_by_email(db, email, current_user.organization_id) or get_user_by_email_is_superuser(db, email):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="User with this email address already exists",
        )
    await countries.get(db, current_user, new_user.country_id)
    db_new_user, password = await insert_new_user(db, current_user, new_user)
    return db_new_user, password
