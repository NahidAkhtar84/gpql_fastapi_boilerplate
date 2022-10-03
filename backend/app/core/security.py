import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.utils import encoding_base64_string
from app.db import models
from app.db import schemas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "ybn11$zjum1=@_tb^7s8do_u$s0h200u08ilorub1b8h&tg*93"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30000
REFRESH_TOKEN_EXPIRE_MINUTES = 1008000


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def create_access_token(domain, user: models.User):
    # print(user.organization_id)
    try:
        meta = dict(user.meta)
        version = meta['version']
    except:
        version = None
    user_obj = schemas.UserTokenBase(version=version, **user.__dict__).dict()
    to_encode = schemas.UserTokenBase.parse_obj(user_obj).dict()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, 'token_type': 'refresh', 'domain': domain})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, expire.strftime('%s')


async def create_refresh_token(domain, user: models.User):
    try:
        meta = dict(user.meta)
        version = meta['version']
    except:
        version = None
    user_obj = schemas.UserTokenBase(version=version, **user.__dict__).dict()
    to_encode = schemas.UserTokenBase.parse_obj(user_obj).dict()

    expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, 'token_type': 'refresh', 'domain': domain})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_access_from_refresh_token(db, refresh_token: str):
    payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    token_data = schemas.RefreshTokenPayload(**payload)
    token_user = db.query(models.User).filter(models.User.email == token_data.email).first()
    try:
        meta = dict(token_user.meta)
        version = meta['version']
    except:
        version = None
    if not version == payload.get('version'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return token_user


async def create_login_token(user: models.User, refresh_token: str):
    try:
        meta = dict(user.meta)
        version = meta['version']
    except:
        version = None
    access_token, exp = await create_access_token(None, user=user)
    ref_token = await create_refresh_token(None, user=user)
    return {
        "access_token": access_token,
        "refresh_token": ref_token,
        "expiry_time": exp
    }


def encoding_token(id: int) -> str:
    token_data = {
        "id": id
    }
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data.update({"exp": expire, 'token_type': 'access'})
    encoded_jwt = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    print("token: ", encoding_base64_string(str(encoded_jwt)))
    return encoding_base64_string(str(encoded_jwt))
