from typing import Optional

from fastapi import APIRouter, Request, Depends, status, HTTPException, Header
from fastapi_pagination import paginate, LimitOffsetPage

from app.api.dependencies.check_permissions import CheckPermission
from app.core.utils import get_all_api_endpoint
from app.db import models, schemas
from app.db.enums import MenuType, ReturnType, Status
from app.db.session import get_db
from app.db.crud import menus
from app.core.auth import get_current_user

menu_router = mr = APIRouter()

menu_check_permission = lambda permission: CheckPermission("menus", permission)


@mr.get(
    "/{menu_id}",
    response_model=schemas.MenuView,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(menu_check_permission("view"))],
)
async def menu_get(
        menu_id: int,
        db=Depends(get_db),
        current_user=Depends(get_current_user),
        x_language_code: Optional[str] = Header("en")
):
    """
    Single view  menu information
    """
    return await menus.get(db, current_user, menu_id)


@mr.post(
    "",
    response_model=schemas.MenuDetailView,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(menu_check_permission("create"))],
)
async def menu_create(
        request: Request,
        menu: schemas.MenuCreate,
        db=Depends(get_db),
        current_user=Depends(get_current_user),
):
    """
    Create a new Menu
    """
    await menus.check_data_validation(db, menu)
    if menu.menu_type == MenuType.PARENT.value:
        menu.parent_menu = None
    if menu.api_end_point is not None and menu.api_end_point.strip():
        api_end_point_set, url_method_dict = get_all_api_endpoint(request)
        api_end_point_list = list(api_end_point_set)
        if menu.api_end_point not in api_end_point_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid api end point"
            )
    db_menu = await menus.create(
        db,
        current_user,
        obj_in=menu,
        unique_field=("api_end_point", "module_id") if menu.api_end_point else (),
    )
    db_permission = models.Permission(menu_id=db_menu["data"].id, group_id=1)
    db.add(db_permission)
    db.commit()
    return db_menu


@mr.get(
    "",
    response_model=LimitOffsetPage[schemas.MenuView],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(menu_check_permission("list"))],
)
async def menu_list(
        request: Request,
        db=Depends(get_db),
        current_user=Depends(get_current_user),
        x_language_code: Optional[str] = Header("en")
):
    """
    Get all menu
    """
    return paginate(
        await menus.get_all(
            db, current_user, query_params=dict(request.query_params)
        )
    )


@mr.put(
    "/{menu_id}",
    response_model=schemas.MenuDetailView,
    response_model_exclude_none=True,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(menu_check_permission("edit"))],
)
async def menu_edit(
        request: Request,
        menu_id: int,
        menu: schemas.MenuUpdate,
        db=Depends(get_db),
        current_user=Depends(get_current_user),
        x_language_code: Optional[str] = Header("en")
):
    """
    Update existing menu
    """
    update_data = menu.dict(exclude_unset=True)
    if update_data["menu_type"] == MenuType.PARENT.value:
        update_data["parent_menu"] = None
        menu.parent_menu = None
    await menus.check_data_validation(db, menu)
    menu_data = await menus.get_data(db, ReturnType.SINGLE.value, id=menu_id)
    if not menu_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Menu data not  found"
        )
    if update_data["menu_type"] == MenuType.CHILD.value:
        if menu_data.menu_type == MenuType.PARENT.value:
            parent_id = await menus.find_root_parent(db, update_data["parent_menu"])
            if parent_id == menu_id:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Circular error of this input.Please insert other parent",
                )
        elif menu_data.menu_type == MenuType.CHILD.value:
            if menu_data.parent_menu != menu.parent_menu:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Already child in this menu.",
                )
    else:
        menu.parent_menu = None
    if menu.api_end_point is not None and menu.api_end_point.strip():
        api_end_point_set, url_method_dict = get_all_api_endpoint(request)
        api_end_point_list = list(api_end_point_set)
        if menu.api_end_point not in api_end_point_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid api end point"
            )
    # print(obj_in)
    return await menus.update(
        db,
        current_user,
        id=menu_id,
        obj_in=menu,
        unique_field=("api_end_point", "module_id") if menu.api_end_point else (),
    )


@mr.delete(
    "/{menu_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(menu_check_permission("delete"))],
)
async def menu_delete(
        menu_id: int,
        db=Depends(get_db),
        current_user=Depends(get_current_user),
        x_language_code: Optional[str] = Header("en")
):
    """
    Delete existing menu
    """
    return await menus.remove(db, current_user, id=menu_id)
