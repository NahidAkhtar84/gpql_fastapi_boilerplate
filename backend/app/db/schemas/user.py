import re
from typing import Optional, Text, Dict, List
from datetime import date
from pydantic import BaseModel, EmailStr, validator, Json
from fastapi import HTTPException, status
from .country import CountryLite
from .group import GroupLite


class UserCommon(BaseModel):
    username: str
    phone: str = None
    full_name: str = None


class UserBase(UserCommon):
    email: EmailStr
    # version: str = None


class UserTokenBase(UserCommon):
    email: EmailStr
    version: str = None


class UserCreate(UserBase):
    password: str
    country_id: int
    city_id: int = None
    user_group: List[int] = []

    @validator('password')
    def validate_password(cls, password):
        if len(password) < 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="password must be at least 4 characters long."
            )
        return password


class UserSelfUpdate(UserCommon):
    country_id: int
    city_id: int = None
    is_citizen: bool = True
    citizen_country_id: int = None
    date_of_birth: date = None
    street_address: str = None
    postal_code: int = None


class UserEdit(UserSelfUpdate):
    user_group: List[int] = []

    class Config:
        orm_mode = True


class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserViewResponse(UserBase):
    id: int
    country: CountryLite

    class Config:
        orm_mode = True


class UserActionResponse(BaseModel):
    detail: str
    data: UserResponse


class UserSignUPBase(UserSelfUpdate):
    email: EmailStr
    password: str

    @validator('password')
    def validate_password(cls, password):
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="password must be at least 8 characters long."
            )
        return password


class UserLogin(BaseModel):
    email: str
    password: str


class SignupResponse(UserBase):
    access_token: str
    refresh_token: str
    token_type: str
    expiry_time: str = None
    permissions: List = None


class LoginResponse(SignupResponse):
    pass


class RefreshToken(BaseModel):
    refresh_token: str


class PasswordBase(BaseModel):
    new_password: str
    confirm_password: str

    @validator('new_password')
    def validate_password(cls, new_password):
        if len(new_password) < 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="password must be at least 4 characters long."
            )
        return new_password

    class Config:
        orm_mode = True


class PasswordChange(PasswordBase):
    previous_password: str

    class Config:
        orm_mode = True


class ResetPassword(PasswordBase):
    class Config:
        orm_mode = True


class ForgetPassword(BaseModel):
    email: EmailStr

    class Config:
        orm_mode = True


class SenderLite(BaseModel):
    id: int = None
    full_name: str = None

    class Config:
        orm_mode = True


class UserLite(BaseModel):
    id: int
    username: str = None
    full_name: str = None

    class Config:
        orm_mode = True


class UserCreateBase(BaseModel):
    email: EmailStr
    user_name: str
    country_id: int
    phone: str = None
    user_group: List[int]

    class Config:
        orm_mode = True
