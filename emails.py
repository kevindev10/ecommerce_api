from fastapi import FastAPI
from starlette.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel, SecretStr
from typing import List
from config import settings
import models
import jwt

# Pydantic model for validating recipient email addresses
class EmailSchema(BaseModel):
    email: List[EmailStr]

# Email server configuration using environment variables from settings
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

# FastAPI app instance (not strictly needed here, but included for completeness)
app = FastAPI()

# Async function to send a verification email to a new user
async def send_email(email: EmailSchema, instance: models.User): 
    """
    Sends an account verification email to the specified user.

    Args:
        email (EmailSchema): Pydantic model containing a list of recipient email addresses.
        instance (models.User): The user instance for whom the email is being sent.

    Returns:
        None
    """
    # Prepare token data for email verification
    token_data = {
        "id": instance.id,
        "email": instance.email,
    }

    # Generate a JWT token for email verification
    token = jwt.encode(token_data, settings.secret, algorithm="HS256")

    # HTML template for the verification email
    template = f"""
        <!DOCTYPE html>
        <html>
        <head></head>
        <body>
            <div style="display: flex; justify-content: center; align-items: center; flex-direction: column;">
                <h3>Account Verification</h3>
                <br>
                <p>Thanks for choosing SokoKubwa Ecommerce, click the button below to verify your account:</p>
                <a href="http://localhost:8000/verification/?token={token}" 
                   style="margin-top: 1rem; padding: 1rem; background-color: #0275d8; color: white; text-decoration: none; border-radius: 0.5rem; font-size: 1rem;">
                    Verify your email
                </a>
                <p>Please ignore this email if you did not register for SokoKubwa Ecommerce.</p>
            </div>
        </body>
        </html>
    """
    
    # Create the email message
    message = MessageSchema(
        subject="SokoKubwa Ecommerce Account Verification Email",
        recipients=email.email,  # List of recipient email addresses
        body=template,           # HTML body of the email
        subtype=MessageType.html,
    )

    # Initialize FastMail with the configuration and send the email
    fm = FastMail(conf)
    await fm.send_message(message)