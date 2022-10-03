from app.db import models, schemas
from .base import BasicCrud


class CountryCRUD(BasicCrud[models.Country, schemas.CountryCreate, schemas.CountryUpdate]):
    pass


countries = CountryCRUD(models.Country)
