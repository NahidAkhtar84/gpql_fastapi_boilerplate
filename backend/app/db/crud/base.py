import pytz, datetime
from typing import Any, Dict, Generic, List, Optional, Tuple, Type, TypeVar, Union

from sqlalchemy.orm import Session
from sqlalchemy.sql import exists
from fastapi import status, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4, BaseModel

from app.db.enums import Status, ReturnType
from app.db.session import Base
from app.db import models

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BasicCrud(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_all(self, db: Session, current_user, query_params: Dict = {}) -> List[ModelType]:
        queryset = db.query(self.model).filter(self.model.deleted_at == None)
        search = query_params.get('search')
        if search:
            search = "%{}%".format(search)
            queryset = queryset.filter(self.model.name.ilike(search))
        queryset = queryset.order_by("created_at").all()
        for data in queryset:
            if data.status:
                data.status = Status(data.status).name
        return queryset

    async def get_data(self, db: Session, return_type, **kwargs):
        obj = db.query(self.model).filter(self.model.deleted_at == None)

        obj = obj.filter_by(**kwargs)
        if return_type == ReturnType.SINGLE.value:
            return obj.first()

        if return_type == ReturnType.COUNT.value:
            return obj.count()
        obj = obj.order_by("created_at").all()
        for data in obj:
            data.status = Status(data.status).name
        return obj

    async def get(self, db: Session, current_user, id: int, **kwargs) -> Optional[ModelType]:

        try:
            data = await self.get_data(db, ReturnType.SINGLE.value, id=id, **kwargs)
            if not data:
                raise
            if data.status:
                data.status = Status(data.status).name
            return data
        except:
            errors_res = await self.response_data(
                data=None, custom_message=f"{self.model.__name__} data not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=errors_res)

    async def create(
            self, db: Session,
            current_user=None,
            *,
            obj_in: CreateSchemaType,
            unique_field: Tuple = ()
    ) -> ModelType:
        await self.check_unique(db, obj_in, None, unique_field)
        try:
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_in_data)
            db_obj.created_by_id = current_user.id if current_user else None
            db_obj.updated_by_id = current_user.id if current_user else None
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return self.response_data(data=db_obj, custom_message=f"Successfully created {self.model.__name__} data")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def update(
            self, db: Session,
            current_user=None,
            *,
            id: int,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]],
            unique_field: Tuple = ()
    ) -> ModelType:
        await self.check_unique(db, obj_in, id, unique_field)
        db_obj = await self.get_data(db, ReturnType.SINGLE.value, id=id)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"{self.model.__name__} data not found")

        obj_data = jsonable_encoder(db_obj)

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data and update_data[field]:
                setattr(db_obj, field, update_data[field])
        db_obj.updated_by_id = current_user.id if current_user else None
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return self.response_data(data=db_obj, custom_message=f"Successfully Updated {self.model.__name__} data")

    async def remove(self, db: Session, current_user=None, *, id: int) -> ModelType:
        obj = await self.get_data(db, ReturnType.SINGLE.value, id=id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data Not Found"
            )
        try:
            obj.deleted_at = datetime.datetime.now(tz=pytz.timezone('UTC'))
            obj.deleted_by_id = current_user.id if current_user else None
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return {f"detail": f"Deleted Successfully {self.model.__name__} data"}
        except:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Dependent data present, can't be deleted")

    def response_data(self, data, custom_message=None):

        if data is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=custom_message if custom_message else "No data found")
        else:
            response_data = {
                "detail": custom_message,
                "data": data
            }
            return response_data

    async def check_unique(self, db: Session, obj_data, id, unique_field: Tuple = ()):
        if len(unique_field) > 0:
            search_args = [getattr(self.model, col) == getattr(
                obj_data, col) for col in unique_field]
            obj = db.query(self.model).filter(*search_args, self.model.deleted_at == None)
            if id:
                obj = obj.filter(self.model.id != id)
            if obj.count():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Unique data already exist in this {self.model.__name__} model"
                )
        return True


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()

    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        session.refresh(instance)
        return instance


def get_model(session, model, **kwargs):
    return session.query(model).filter_by(**kwargs).first()
