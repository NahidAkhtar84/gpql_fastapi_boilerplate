from app.db.session import SessionLocal
from app.core.const import MODULE_LIST, ORGANIZATION_LIST, GROUP_LIST
from app.db.crud import get_or_create
from app.db import models


def init():
    db = SessionLocal()


def create_organization():
    db = SessionLocal()
    for organization in ORGANIZATION_LIST:
        get_or_create(db, models.Organization, name=organization, domain=organization.lower(), status=1)


def create_group():
    db = SessionLocal()
    for group in GROUP_LIST:
        get_or_create(db, models.Group, id=group, name=GROUP_LIST[group], status=1, is_protected=True)


def create_module():
    db = SessionLocal()
    for module in MODULE_LIST:
        get_or_create(db, models.Module, id=module, name=MODULE_LIST[module], status=1)


if __name__ == "__main__":
    create_organization()
    create_group()
    create_module()
