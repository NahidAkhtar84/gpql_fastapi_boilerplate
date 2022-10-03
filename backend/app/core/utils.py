import base64
import jwt
import os
import uuid
import shutil
import re
from itertools import groupby
from fastapi import status, HTTPException, UploadFile

from app.core import security
from app.core.const import METHOD_TYPE
from app.db import schemas

ALLOWED_FILE_EXTENSIONS = ['jpg', 'jpeg', 'png']


def encoding_base64_string(value: str) -> str:
    value_bytes = value.encode('ascii')
    base64_bytes = base64.b64encode(value_bytes)
    base64_value = base64_bytes.decode('ascii')
    return base64_value


def decoding_base64_string(base64_value: str) -> str:
    base64_bytes = base64_value.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    value = message_bytes.decode('ascii')
    return value


def verify_token_by_get_id(token: str) -> int:
    try:
        payload = payload = jwt.decode(
            str(decoding_base64_string(token)), security.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        user_id = payload.get('id')
    except:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid or expired token"
        )
    return user_id


def file_upload(file: UploadFile, upload_path: str) -> str:
    real_file_size = 0
    # for chunk in file.file:
    #     real_file_size += len(chunk)
    #     if real_file_size > 500000:
    #         raise HTTPException(
    #             status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
    #             detail="Image size is too large. Please upload image less than 500 kb"
    #         )
    filename = file.filename
    split_file_name = os.path.splitext(filename)
    file_extension = split_file_name[1].split('.')[-1]
    if file_extension.lower() not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Image type must be one of {', '.join(ALLOWED_FILE_EXTENSIONS)}"
        )
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    new_name = f"{str(uuid.uuid4().hex)}.{file_extension}"
    file_location = f"{upload_path}/{new_name}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_location


def number_format(number, decimal_point=5):
    if (decimal_point == None):
        return number
    else:
        return round(number, decimal_point)


def remove_special_sentence(sentence, character):
    return ''.join(character if a == character else ''.join(b) for a, b in groupby(sentence))


def get_all_api_endpoint(request):
    api_end_point_set = set()
    url_method_dict = {}
    for route in request.app.routes:
        if re.search("api/v1", str(route.path)):
            tags = str(route.tags[0]).lower()
            if not tags == "public" and not tags == "auth":
                path = route.path
                for key in route.param_convertors.keys():
                    key = "/{" + key + "}"
                    path = path.replace(key, "")
                path = remove_special_sentence(path, "/")
                path = path.replace("/api/v1/", "")
                path = path.replace("/", "_")
                api_end_point_set.add(path)
                if not path in url_method_dict:
                    url_method_dict[path] = []
                methods = list(route.__dict__.get('methods'))

                method_type = METHOD_TYPE[methods[0].lower()]
                if method_type == 'view' and not route.param_convertors:
                    method_type = 'list'
                url_method_dict[path].append(method_type)
    return api_end_point_set, url_method_dict

