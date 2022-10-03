from sqlalchemy import Boolean, Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import Session, relationship

from app.db.session import Base, get_db
from app.db.models.common_base import DecendentCommonBase


class Module(Base, DecendentCommonBase):

    name = Column(String, nullable=False)

    menus = relationship("Menu", back_populates="module")
