COUNTRY_FILE_UPLOAD_PATH = 'media/country'

UNIQUE_CODE_DIGIT = 12
ORGANIZATION_LIST = ["Vivasoft"]
GROUP_LIST = {
    1: "Super Admin",
    2: "Admin",
    3: "Customer"
}
GROUP_LIST_REVERSE = dict((v, k) for k, v in GROUP_LIST.items())

MODULE_LIST = {
    1: "Admin Management",
    2: "Customer Management"
}
METHOD_TYPE = {
    "post": "create",
    "put": "edit",
    "patch": "edit",
    "delete": "delete",
    "get": "view"
}
# Upload Max Size
IMAGE_UPLOAD_MAX_SIZE = 500000  # 500kb
VIDEO_UPLOAD_MAX_SIZE = 4000000  # 4 mb
