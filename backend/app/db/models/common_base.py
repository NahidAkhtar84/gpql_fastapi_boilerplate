import datetime
import pytz
from typing import Dict, Any
import inflect
import re

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

from app.db.enums import Status


def current_time():
    return datetime.datetime.now(tz=pytz.timezone('UTC'))


inflect = inflect.engine()


class CommonBase:
    __name__: str

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=current_time, nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=current_time, nullable=False,
        onupdate=current_time
    )
    deleted_at = Column(
        DateTime(timezone=True)
    )
    status = Column(Integer, nullable=True, default=Status.ACTIVE.value)

    @classmethod
    def get_table_name(cls, make_plural: bool = True):
        _name = f"{cls.__name__}"
        _name = " ".join(re.split("(?=[A-Z])", _name)).split()
        _name[-1] = _name[-1] if inflect.singular_noun(_name[-1]) else inflect.plural(_name[-1])
        _name = " ".join(_name).replace(" ", "_").lower()
        return _name

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.get_table_name()


class DecendentCommonBase(CommonBase):
    @declared_attr
    def created_by_id(cls):
        return Column(Integer, ForeignKey('users.id'))

    @declared_attr
    def updated_by_id(cls):
        return Column(Integer, ForeignKey('users.id'))

    @declared_attr
    def deleted_by_id(cls):
        return Column(Integer, ForeignKey('users.id'))

    @declared_attr
    def created_by(cls):
        return relationship("User", foreign_keys=f"{cls.__name__}.created_by_id")

    @declared_attr
    def updated_by(cls):
        return relationship("User", foreign_keys=f"{cls.__name__}.updated_by_id")

    @declared_attr
    def deleted_by(cls):
        return relationship("User", foreign_keys=f"{cls.__name__}.deleted_by_id")


class SimpleCommonBase(DecendentCommonBase):
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
