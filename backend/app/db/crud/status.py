from starlette import status
from fastapi import HTTPException

from sqlalchemy.orm import Session
from app.db import enums


def make_list_to_dictionary(statusClass):
    statuses = []
    for enum in statusClass:
        statuses.append((str(enum.name), int(enum.value)))
    return dict(statuses)


def status_types_get():
    status_types = {
        'status': make_list_to_dictionary(enums.Status),
        'menu_type': make_list_to_dictionary(enums.MenuType),
        'credit_or_debit': make_list_to_dictionary(enums.CreditOrDebit),
        'charge_type': make_list_to_dictionary(enums.ChargeType),
        'transaction_status': make_list_to_dictionary(enums.TransactionStatus),
        'payment_status': make_list_to_dictionary(enums.PaymentStatus),
        'payment_receive_status': make_list_to_dictionary(enums.PaymentReceiveStatus),
        'commission_status': make_list_to_dictionary(enums.CommissionStatus)
    }
    return status_types
