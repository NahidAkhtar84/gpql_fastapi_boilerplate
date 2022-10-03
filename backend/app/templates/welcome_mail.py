from app.core.config import MAIL_SEND_COMMON_URL


def welcome_mail(welcome_data):
    template = f"""
            <!DOCTYPE html>
            <html>
            <head>
            </head>
            <body>
                <div style=" display: flex; align-items: center; justify-content: center; flex-direction: column;">
                    <h3> Welcome to </h3>
                    <br>
                    <p>Hi {welcome_data['data'].username}</p> 
                    <p>Your account is successfully created.please click on the link and login.</p>
                    <a style="margin-top:1rem; padding: 1rem; border-radius: 0.5rem; font-size: 1rem; text-decoration: none; background: #0275d8; color: white;"
                     # href="{MAIL_SEND_COMMON_URL}/login">
                        login
                    <a>
                    <p>Your login information:</p>
                    <h3>email: {welcome_data['data'].email}
                    <h3>password: {welcome_data['password']}
                </div>
            </body>
            </html>
        """
    return template
