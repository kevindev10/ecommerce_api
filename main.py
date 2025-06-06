from fastapi import FastAPI, Depends, Request, HTTPException, status, BackgroundTasks
import os

from fastapi.responses import HTMLResponse
import models, schemas, authentication
from database import engine, get_db
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.event import listens_for
from authentication import hash_password, verify_token
from fastapi.templating import Jinja2Templates
import emails

# Create all models in the database
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return {"message": "Hello World"}


# Automatically create a Business for each new User registration
# Listen for new User inserts and trigger business creation automatically
@listens_for(models.User, "after_insert")
def create_business(mapper, connection, target):
    # Create a new database session using the current transaction connection
    db = Session(bind=connection)  
    
    # Instantiate a new Business linked to the registered User
    business_obj = models.Business(business_name=target.username, owner_id=target.id)
    
    # Add the new Business instance to the session
    db.add(business_obj)  
    
    # Commit the transaction to save the new Business in the database
    db.commit()  
    
    # Close the session to free up resources and avoid connection leaks
    db.close()  


@app.post("/registration")
async def user_registration(
    user: schemas.UserCreate,
    background_tasks: BackgroundTasks,  
    db: Session = Depends(get_db)
):
    # Hash password
    hashed_password = authentication.hash_password(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Schedule the email to be sent in the background
   
    background_tasks.add_task(emails.send_email, emails.EmailSchema(email=[new_user.email]), new_user)

    return {
        "status": "Ok",
        "data": f"Hello {new_user.username}, thanks for choosing our services. Please check your inbox for the confirmation email."
    }



@app.get("/verification", response_class=HTMLResponse)
async def email_verification(request: Request, token:str, db: Session = Depends(get_db)):
    user = await authentication.verify_token(token)
    
    if user and not user.is_verified:
        user.is_verified = True
        db.add(user)  # optional, but doesn't hurt
        db.commit()
        db.refresh(user)
        return templates.TemplateResponse("verification.html", {"request": request, "username": user.username})
    
    raise HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"}
    )