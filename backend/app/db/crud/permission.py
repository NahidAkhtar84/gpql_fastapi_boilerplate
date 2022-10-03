from typing import List, Dict

from fastapi import HTTPException, status, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db import models, schemas
from app.db.enums import MenuType
from app.db.crud import menus, modules
from ..enums import ReturnType, Status
from .base import BasicCrud
from ...core.utils import get_all_api_endpoint


class PermissionCRUD(BasicCrud[models.Permission, schemas.PermissionCreate, schemas.PermissionCreate]):
    async def set_permission(
            self, db: Session, request,
            permission_data: schemas.PermissionCreate
    ) -> List[schemas.PermissionMenuView]:
        data = permission_data.dict(exclude_unset=True)
        permission_update_list = []
        permission_list = []
        menu_dict = {}
        api_end_point_set, url_method_dict = get_all_api_endpoint(request)
        for menu in data['menu_permission']:
            menu_data = await menus.get_data(
                db, ReturnType.SINGLE.value,
                id=menu['menu_id'],
                module_id=permission_data.module_id,
                status=Status.ACTIVE.value
            )
            if not menu_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"This {menu['menu_id']}'s id dose not add in this permission"
                )
            permission = await self.get_data(
                db, ReturnType.SINGLE.value,
                group_id=permission_data.group_id,
                menu_id=menu_data.id
            )
            permission_operation_dict = schemas.PermissionOperation(**menu).dict()
            for _dict in permission_operation_dict.keys():
                if _dict not in url_method_dict.get(menu_data.api_end_point, {}):
                    menu[str(_dict)] = False
            menu['status'] = Status.ACTIVE.value
            menu['group_id'] = data['group_id']
            menu_dict[str(menu_data.id)] = menu_data
            if permission:
                menu['id'] = permission.id
                permission_update_list.append(self.model(**menu))
            else:
                permission_list.append(self.model(**menu))
        if len(permission_list) > 0:
            db.add_all(permission_list)
            db.commit()
        if len(permission_update_list) > 0:
            db.bulk_update_mappings(self.model, jsonable_encoder(permission_update_list))
        db.commit()

        return {"detail": "Successfully set Permissions"}

    async def get_module_and_group_based_permission(
            self, db: Session, request,
            group_data: models.Group,
            module_data: models.Module,
    ) -> List[schemas.PermissionMenuView]:
        db_menus = await menus.get_data(db, ReturnType.ALL.value, module_id=module_data.id, status=Status.ACTIVE.value)
        menu_list = []
        all_permission_dict = {}
        api_end_point_set, url_method_dict = get_all_api_endpoint(request)
        for data in db_menus:
            menu_list.append(data.id)
            permission_dict = {
                method: True if group_data.id == 1 else False for method in url_method_dict.get(data.api_end_point, {})
            }
            all_permission_dict[data.id] = permission_dict
        db_all_permission = db.query(self.model).filter(
            self.model.group_id == group_data.id,
            self.model.menu_id.in_(menu_list),
            self.model.deleted_at == None
        )
        for data in db_all_permission:
            permission_data = schemas.PermissionOperation(**data.__dict__).dict()
            for _dict in all_permission_dict[data.menu_id].keys():
                all_permission_dict[data.menu_id][str(_dict)] |= permission_data[str(_dict)] \
                    if permission_data[str(_dict)] else False
        all_permission_list = []
        for data in db_menus:
            all_permission_list.append(
                schemas.PermissionMenuView(
                    id=data.id,
                    menu_name=data.name,
                    **all_permission_dict[data.id]
                )
            )
        return all_permission_list

    def get_default_login_permission_response_data(self, menu_data):
        menu_dict = {
            "id": menu_data.id,
            "name": menu_data.name,
            "url": menu_data.menu_url,
            "icon": menu_data.menu_icon,
            "parent_id": menu_data.parent_menu,
            "menu_serial": menu_data.menu_serial,
            "can_create": False,
            "can_edit": False,
            "can_view": False,
            "can_list": False,
            "can_delete": False
        }
        return menu_dict

    def get_login_permission_response_data(self, current_user, menu_dict, data, url_method_type: Dict = {}):
        menu_dict["can_create"] |= False if 'create' not in url_method_type else (
            True if current_user.is_superuser else data.create
        )
        menu_dict["can_edit"] |= False if 'edit' not in url_method_type else (
            True if current_user.is_superuser else data.edit
        )
        menu_dict["can_view"] |= False if 'view' not in url_method_type else (
            True if current_user.is_superuser else data.view
        )
        menu_dict["can_list"] |= False if 'list' not in url_method_type else (
            True if current_user.is_superuser else data.list
        )
        menu_dict["can_delete"] |= False if 'delete' not in url_method_type else (
            True if current_user.is_superuser else data.delete
        )
        return menu_dict

    def delete_not_peemitted_permission(self, menu_dict):
        if not menu_dict["can_create"]:
            del menu_dict["can_create"]
        if not menu_dict["can_edit"]:
            del menu_dict["can_edit"]
        if not menu_dict["can_view"]:
            del menu_dict["can_view"]
        if not menu_dict["can_list"]:
            del menu_dict["can_list"]
        if not menu_dict["can_delete"]:
            del menu_dict["can_delete"]
        return menu_dict

    def get_all_parent_menu(self, db, menu: models.Menu, parent_menu_list=[]):
        if menu.parent_menu and menu.parent_menu not in parent_menu_list:
            db_parent_menu = db.query(models.Menu).filter(models.Menu.id == menu.parent_menu).first()
            parent_menu_list.append(db_parent_menu.id)
            return self.get_all_parent_menu(db, db_parent_menu, parent_menu_list)
        return parent_menu_list

    async def get_permissions_by_user_login(self, db, request, current_user):
        db_permission = db.query(self.model).filter(self.model.deleted_at == None)
        if not current_user.is_superuser:
            permission_subquery = db.query(self.model).filter(
                or_(
                    self.model.create == True,
                    self.model.edit == True,
                    self.model.view == True,
                    self.model.list == True,
                    self.model.delete == True
                ),
                self.model.group_id.in_(current_user.group_id_list),
                self.model.deleted_at == None
            ).all()
            parent_menu_list = []
            for data in permission_subquery:
                parent_menu_list.append(data.menu_id)
                parent_menu_list = self.get_all_parent_menu(db, data.menu, parent_menu_list)
            db_permission = db_permission.filter(
                or_(
                    self.model.create == True,
                    self.model.edit == True,
                    self.model.view == True,
                    self.model.list == True,
                    self.model.delete == True,
                    self.model.menu_id.in_(parent_menu_list)
                ),
                self.model.group_id.in_(current_user.group_id_list)
            )

        all_menu_dict = {}
        all_module_dict = {}
        menu_id_list = []
        menu_data_list = []
        module_id_list = []
        specific_permission = []
        api_end_point_set, url_method_dict = get_all_api_endpoint(request)
        for data in db_permission.order_by(self.model.menu_id.asc()).all():
            if data.menu_id not in menu_id_list:
                menu_id_list.append(data.menu_id)
                menu_data_list.append(data.menu)
                all_menu_dict[data.menu_id] = self.get_default_login_permission_response_data(data.menu)
            all_menu_dict[data.menu_id] = self.get_login_permission_response_data(
                current_user,
                all_menu_dict[data.menu_id],
                data,
                url_method_dict.get(str(data.menu.api_end_point), {})
            )
        for id in menu_id_list:
            all_menu_dict[id] = self.delete_not_peemitted_permission(all_menu_dict[id])
        db_active_menu = db.query(models.Menu).filter(
            models.Menu.id.in_(menu_id_list),
            models.Menu.status == Status.ACTIVE.value,
            models.Menu.deleted_at == None,
            models.Menu.menu_type != MenuType.EXTRA.value
        ).order_by(models.Menu.menu_serial).all()
        menu_id_list = [data.id for data in db_active_menu]
        for data in menu_data_list:
            if data.id in menu_id_list:
                if data.module_id not in module_id_list:
                    module_id_list.append(data.module_id)
                    all_module_dict[data.module_id] = {
                        "id": data.module_id,
                        "module_name": data.module.name,
                        "menu_permission": []
                    }
                all_module_dict[data.module_id]['menu_permission'].append(all_menu_dict[data.id])
        db_active_module = db.query(models.Module).filter(
            models.Module.id.in_(module_id_list),
            models.Module.status == Status.ACTIVE.value,
            models.Module.deleted_at == None
        ).all()
        module_id_list = [data.id for data in db_active_module]
        for id in module_id_list:
            all_module_dict[id]["menu_permission"] = sorted(
                all_module_dict[id]["menu_permission"], key=lambda _dict: _dict['menu_serial']
            )
            [_permission.pop("menu_serial") for _permission in all_module_dict[id]["menu_permission"]]
            specific_permission.append(all_module_dict[id])
        return specific_permission


permissions = PermissionCRUD(models.Permission)
