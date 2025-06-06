from fastapi import FastAPI
from starlette.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel, SecretStr
from typing import List
from config import settings
import models
import jwt

class EmailSchema(BaseModel):
    email: List[EmailStr]


conf = ConnectionConfig(
    MAIL_USERNAME = settings.mail_username,
    MAIL_PASSWORD = SecretStr(settings.mail_password),
    MAIL_FROM = settings.mail_from,
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_FROM_NAME="Ecommerce_API",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

app = FastAPI()



async def send_email(email: EmailSchema, instance:models.User): 

    token_data = {
        "id": instance.id,
        "email": instance.email,
    }

    token = jwt.encode(token_data, settings.secret, algorithm="HS256")

    template = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        
                    </head>
                    <body>
                        <div style="display: flex; justify-content: center; align-items: center; flex-direction: column;">

                            <h3> Account Verification </h3>
                            <br>
                            <p>Thanks for choosing SokoKubwa Ecommerce, click the button below to verify you account</p>
                            <a href="http://localhost:8000/verification/?token={token}" style="margin-top: 1rem; padding: 1rem; background-color: #0275d8; color: white; text-decoration: none; border-radius: 0.5rem; font-size: 1rem;">
                                 Verify your email  await fm.send_message(message)
                            <p> Please ignore this email if you did not register for SokoKubwa Ecommerce</p>

                        </div>
                    </body>
                    </html>
                """
    
    message = MessageSchema(
        subject="SokoKubwa Ecommerce Account Verification Email",
        recipients=email.email,  # this now works!
        body=template,           # use your HTML template here
        subtype=MessageType.html,
    )
    fm = FastMail(conf)
    await fm.send_message(message)