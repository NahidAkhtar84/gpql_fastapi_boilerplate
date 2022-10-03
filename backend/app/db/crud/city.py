from app.db import models, schemas

from .base import BasicCrud


class CityCRUD(BasicCrud[models.City, schemas.CityCreate, schemas.CityUpdate]):
    pass


cities = CityCRUD(models.City)

