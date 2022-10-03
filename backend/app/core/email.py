import smtplib
from fastapi import Request
from email.message import EmailMessage
from app.db.enums import MailSendType
from app.core.config import EMAIL_USER, EMAIL_PASSWORD
from app.core.security import encoding_token
from app.templates.verification_mail import verification_mail
from app.templates.reset_password_mail import reset_password_mail
from app.templates.welcome_mail import welcome_mail


def send_email(email, type: int, **kwargs):
    if type == MailSendType.VERIFICATION.value:
        subject = "Verification Mail"
        body = verification_mail(kwargs)
    elif type == MailSendType.PASSWORD_RESET.value:
        subject = "Password Reset"
        token = encoding_token(kwargs['id'])
        body = reset_password_mail( token)
    elif type == MailSendType.NEW_USER_SEND_PASSWORD.value:
        subject = f"Welcome to "
        body = welcome_mail(kwargs)

    # Email Send

    email_message = EmailMessage()
    email_message['subject'] = subject
    email_message['From'] = EMAIL_USER
    email_message['To'] = email
    email_message.add_alternative(body, subtype='html')
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASSWORD)
        smtp.send_message(email_message)
