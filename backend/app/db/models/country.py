from sqlalchemy import Column, String, Text, Integer
from sqlalchemy.orm import Session, relationship

from app.db.session import Base, get_db
from app.db.models.common_base import DecendentCommonBase


class Country(Base, DecendentCommonBase):
    name = Column(String(255), nullable=True)
    code = Column(String(255), nullable=True)
    currency_name = Column(String(255), nullable=True)
    currency_code = Column(String(10), nullable=True)
    currency_number = Column(Integer, nullable=True)
    description = Column(String(255), nullable=True)
    logo = Column(Text, nullable=True)

    cities = relationship("City", back_populates="country")
    
    



