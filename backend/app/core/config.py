import os

PROJECT_NAME = os.getenv("PROJECT_NAME")

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
MAIL_SEND_COMMON_URL = os.getenv("VERIFICATION_URL")

API_STR = "/api/v1"
MAP_URL = lambda route: f"{API_STR}/{route}"
