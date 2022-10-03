from fastapi import HTTPException, status
from app.core import config
from app.core.auth import get_user_by_email
from app.core.security import get_password_hash
from app.db import models, schemas
from app.db.crud import get_or_create, permissions, get_model
from app.db.enums import MenuType
from app.db.session import SessionLocal
from app.scripts.initial_data import create_organization, create_group, create_module


def input_credential() -> tuple:
    email: str = input("email:")
    password: str = input("password:")
    if email and password:
        if '@' not in email:
            print('Incorrect email!')
            input_credential()
        if len(password) < 8:
            print('password length must be atleast 8 character!')
            input_credential()
        db = SessionLocal()
        if get_model(db, models.User, email=email):
            print("User with this email address already exists")
            input_credential()
        return email, password
    print('Incorrect input. please try again!')
    input_credential()


def country(db):
    country_data = get_or_create(
        db,
        models.Country,
        name="Bangladesh",
        code="880",
        currency_name="Tk",
        currency_code="Tk",
        currency_number=1
    )
    return country_data


def init(email: str, password: str) -> None:
    db = SessionLocal()
    hashed_password = get_password_hash(password)
    group_data = get_or_create(db, models.Group, id=1, name="Super Admin", status=1, is_protected=True)
    db_user = models.User(
        email=email,
        username="super_user",
        password=hashed_password,
        country_id=country(db).id,
    )
    db_user.groups.append(group_data)
    db.add(db_user)
    db.commit()
    return "Successfully created super_user"


if __name__ == "__main__":
    promt = input("Create superuser?(y/n): ")
    if promt == 'y':
        email, password = input_credential()
        create_organization()
        create_group()
        create_module()
        init(email, password)
        print("Successfully created superuser")
    else:
        print('Skipped superuser create')
