from typing import Any, Dict

from app.db import models, schemas
from .base import BasicCrud
from ..enums import Status


class ModuleCRUD(BasicCrud[models.Module, schemas.ModuleCreate, schemas.ModuleUpdate]):
    async def get_module_list(self, db, current_user, query_params: Dict = {}):
        module_data = current_user.modules
        search = query_params.get('search')
        if search:
            search = "%{}%".format(search)
            module_data = module_data.filter(self.model.name.ilike(search))
        module_data = module_data.order_by("created_at").all()
        for data in module_data:
            data.status = Status(data.status).name
        return module_data


modules = ModuleCRUD(models.Module)
