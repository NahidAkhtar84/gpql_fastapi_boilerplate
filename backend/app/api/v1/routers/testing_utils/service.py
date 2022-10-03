import random

from faker import Faker

from app.db.enums import Status

fake = Faker()


def get_new_service():
    service = {
        "name": fake.name(),
        "description": fake.name(),
        "status": 1
    }
    return service
