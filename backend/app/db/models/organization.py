from sqlalchemy import Boolean, Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import Session, relationship

from app.db.session import Base, get_db
from app.db.models.common_base import DecendentCommonBase


class Organization(Base, DecendentCommonBase):
    name = Column(String)
    domain = Column(String, unique=True)
