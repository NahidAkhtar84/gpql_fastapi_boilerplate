from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import Session, relationship

from app.db.session import Base, get_db
from app.db.models.common_base import DecendentCommonBase


class City(Base, DecendentCommonBase):
    name = Column(String(255), nullable=True)
    code = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=False)
    
    #relationship
    country = relationship("Country", foreign_keys=[country_id], back_populates="cities")
    