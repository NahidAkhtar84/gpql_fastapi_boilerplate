from sqlalchemy import Boolean, Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import Session, relationship

from app.db.session import Base, get_db
from app.db.models.common_base import DecendentCommonBase


class Group(Base, DecendentCommonBase):
    name = Column(String, nullable=True)
    is_protected = Column(Boolean, default=True)

    permissions = relationship("Permission", back_populates="user_group", lazy='dynamic')
