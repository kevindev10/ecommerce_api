import jwt
from passlib.context import CryptContext
from database import get_db
from config import Settings
import models
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status





# Passlib context for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
def hash_password(password: str):
    return pwd_context.hash(password)


async def verify_token(token: str, db: Session = Depends(get_db)):

    try:
        # Decode the token using the secret key and algorithm
        payload = jwt.decode(token, Settings.secret, algorithms=["HS256"])
        user_id = payload.get("user_id")
        user =  db.query(models.User).filter(models.User.id == user_id).first()


    except:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    return user


# # Verify password
# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)@@