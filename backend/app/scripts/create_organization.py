#!/usr/bin/env python3
from fastapi import HTTPException, status
from app.db import models
from app.db.session import SessionLocal

def input_credential() -> tuple:
    name: str = input("name:")
    if name:
        if len(name) < 3:
            print('Organization name length must be atleast 3 character!')
            input_credential()
        return name
    print('Incorrect input. please try again!')
    input_credential()


def init(name: str) -> None:
    db = SessionLocal()
    if db.query(models.Organization).filter(models.Organization.name==name).first():
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="Organization with this name already exists"
        )
    db_organization = models.Organization(
        name=name,
        status=1
    )
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)

if __name__ == "__main__":
    promt = input("Create organization?(y/n)")
    if promt == 'y':
        name = input_credential()
        init(name)
        print("Organization created")
    else:
        print('Skipped organization create')
