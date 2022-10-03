import random
from enum import Enum


class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    @classmethod
    def random_choice(cls):
        return random.choice(cls.list())


class Status(ExtendedEnum):
    DEACTIVE = 0
    ACTIVE = 1
    PENDING = 2
    OP_PROBITION = 3


class MenuType(ExtendedEnum):
    PARENT = 0
    CHILD = 1


class ReturnType(ExtendedEnum):
    SINGLE = 0
    ALL = 1
    COUNT = 2


class MailSendType(ExtendedEnum):
    VERIFICATION = 0
    PASSWORD_RESET = 1
    NEW_USER_SEND_PASSWORD = 2


