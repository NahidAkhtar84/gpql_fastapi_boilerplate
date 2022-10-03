from sqlalchemy import Boolean, Column, Integer, ForeignKey
from sqlalchemy.orm import Session, relationship
from app.db.session import Base, get_db
from app.db.models.common_base import DecendentCommonBase


class Permission(Base, DecendentCommonBase):
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    menu_id = Column(Integer, ForeignKey('menus.id'), nullable=False)
    create = Column(Boolean, default=False)
    edit = Column(Boolean, default=False)
    view = Column(Boolean, default=False)
    list = Column(Boolean, default=False)
    delete = Column(Boolean, default=False)

    # relationships

    user_group = relationship("Group", back_populates="permissions")
    menu = relationship("Menu", back_populates="permissions")


