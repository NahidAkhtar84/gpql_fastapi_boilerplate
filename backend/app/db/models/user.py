import uuid

from sqlalchemy import Boolean, Column, String, Integer, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import Boolean, Column, String, Integer, Text, ForeignKey, Date
from app.db.session import Base, get_db
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql.schema import Table

from app.db.session import Base, get_db
from app.db.models.common_base import CommonBase

user_and_group_identifier = Table('user_and_group_identifier', Base.metadata,
                                  Column('user_id', Integer(), ForeignKey('users.id')),
                                  Column('group_id', Integer(), ForeignKey('groups.id')))



class User(Base, CommonBase):
    __tablename__ = "users"
    email = Column(String, index=True, nullable=False)
    password = Column(String, nullable=False)
    username = Column(String, nullable=False)
    is_citizen = Column(Boolean, default=True)
    full_name = Column(String)
    phone = Column(String)
    meta = Column(JSON, nullable=True)
    street_address = Column(String)
    postal_code = Column(Integer)
    date_of_birth = Column(Date(), nullable=True)
    is_active = Column(Boolean, default=True)

    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True)
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=False)
    city_id = Column(Integer, ForeignKey('cities.id'))
    citizen_country_id = Column(Integer, ForeignKey('countries.id'))
    created_by_id = Column(Integer, ForeignKey('users.id'))
    updated_by_id = Column(Integer, ForeignKey('users.id'))
    deleted_by_id = Column(Integer, ForeignKey('users.id'))


    # Relationship
    groups = relationship("Group", secondary=user_and_group_identifier, lazy='dynamic')

    organization = relationship("Organization", foreign_keys=[organization_id])
    country = relationship("Country", foreign_keys=[country_id])
    citizen_country = relationship("Country", foreign_keys=[citizen_country_id])
    city = relationship("City", foreign_keys=[city_id])

    created_by = relationship("User", foreign_keys=[created_by_id])
    updated_by = relationship("User", foreign_keys=[updated_by_id])
    deleted_by = relationship("User", foreign_keys=[deleted_by_id])

    @property
    def version_renew(self):
        try:
            meta = dict(self.meta)
        except:
            meta = {}
        meta['version'] = uuid.uuid4().hex
        return meta

    @property
    def is_superuser(self):
        group_list = self.groups
        for data in group_list:
            if data.id == 1:
                return True
        return False

    @property
    def is_admin(self):
        group_list = self.groups
        for data in group_list:
            if data.id == 2:
                return True
        return False

    @property
    def is_customer(self):
        group_list = self.groups
        for data in group_list:
            if data.id == 3:
                return True
        return False

    @property
    def group_id_list(self):
        return [group.id for group in self.groups]

