import phonenumbers
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import or_
from fastapi import HTTPException, status, BackgroundTasks
from app.db.enums import Status, ReturnType

from app.db import models


def search_with_params(queryset, search, model):
    search = "%{}%".format(search)
    queryset = queryset.filter(
        or_(model.name.ilike(search),
            model.email.ilike(search)
            ))
    return queryset


def phone_number_validation_check(db, user) -> str:
    if user.phone:
        user.phone = str(''.join([n for n in user.phone if n.isdigit() or n == '+']))
        print(user.phone)
        try:
            phone = phonenumbers.parse(user.phone)
            if phonenumbers.is_valid_number(phone):
                if str(phone.country_code) == db.query(models.Country).filter(
                        models.Country.id == user.country_id
                ).first().code:
                    return user.phone
            raise
        except:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid phone number, please, provide a valid phone number based on the country you have selected!",
            )
    else:
        return None


async def get_model_info(db: Session, model, return_type, **kwargs):
        obj = db.query(model).filter(model.deleted_at == None)
        
        obj = obj.filter_by(**kwargs)
        if return_type == ReturnType.SINGLE.value:
            response = obj.first()
            if not response:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{model.__name__} data not found!"
                )
            else:
                return response
        
        if return_type == ReturnType.COUNT.value:
            return obj.count()
        obj = obj.order_by("created_at").all()
        for data in obj:
            data.status = Status(data.status).name
        return obj

