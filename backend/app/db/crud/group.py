from app.db import models, schemas
from .base import BasicCrud


class GroupCRUD(BasicCrud[models.Group, schemas.GroupCreate, schemas.GroupUpdate]):
    pass


groups = GroupCRUD(models.Group)
