from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import Session, relationship

from app.db.enums import MenuType
from app.db.session import Base, get_db
from app.db.models.common_base import DecendentCommonBase


class Menu(Base, DecendentCommonBase):
    name = Column(String(255), nullable=True)
    module_id = Column(Integer, ForeignKey('modules.id'))
    menu_type = Column(Integer, nullable=True, default=MenuType.PARENT.value)
    parent_menu = Column(Integer, ForeignKey('menus.id'))
    menu_serial = Column(Integer, nullable=True)
    api_end_point = Column(String(255), nullable=True)
    menu_icon = Column(String(255), nullable=True)
    menu_url = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)

    # relationships
    parent = relationship("Menu", foreign_keys=[parent_menu])
    module = relationship("Module", foreign_keys=[module_id], back_populates='menus')
    permissions = relationship("Permission", back_populates="menu")
