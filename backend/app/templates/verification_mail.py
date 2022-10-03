from app.core.config import MAIL_SEND_COMMON_URL
from app.core.security import encoding_token


def verification_mail(data):
    template = f"""
            <!DOCTYPE html>
            <html>
            <head>
            </head>
            <body>
                <div style=" display: flex; align-items: center; justify-content: center; flex-direction: column;">
                    <h3> Account Verification </h3>
                    <br>
                    <p>Thanks for choosing ......, please 
                    click on the link below to verify your account</p> 
                    <a style="margin-top:1rem; padding: 1rem; border-radius: 0.5rem; font-size: 1rem; text-decoration: none; background: #0275d8; color: white;"
                     # href="{MAIL_SEND_COMMON_URL}/verification/{encoding_token(data['id'])}">
                        Verify your email
                    <a>
                    <p style="margin-top:1rem;">If you did not register for STS, 
                    please kindly ignore this email and nothing will happen. Thanks<p>
                </div>
            </body>
            </html>
        """
    return template
