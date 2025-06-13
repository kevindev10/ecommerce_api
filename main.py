from fastapi import FastAPI, Depends, Request, HTTPException, status, BackgroundTasks
import os
import jwt
from fastapi.responses import HTMLResponse
import models, schemas, authentication
from database import engine, get_db
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.event import listens_for
from authentication import token_generator,authenticate_user, verify_token
from fastapi.security import (OAuth2PasswordBearer, OAuth2PasswordRequestForm)
from fastapi.templating import Jinja2Templates
from config import settings
import emails
from fastapi import File, UploadFile
import secrets
from fastapi.staticfiles import StaticFiles
from PIL import Image
from fastapi.encoders import jsonable_encoder






# Create all models in the database
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# authorization configs
oath2_scheme = OAuth2PasswordBearer(tokenUrl = 'token')



async def get_current_user(token: str = Depends(oath2_scheme), db: Session = Depends(get_db)):
    try:
        # Decode the token using the secret key and algorithm
        payload = jwt.decode(token, settings.secret, algorithms=["HS256"])
        user_id = payload.get("id")
        user = db.query(models.User).filter(models.User.id == user_id).first()
    except:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            detail = "Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


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
async def email_verification(request: Request, token: str, db: Session = Depends(get_db)):
    user = await authentication.verify_token(token, db)  # <-- pass db here!
    if user and not user.is_verified:
        user.is_verified = True
        db.add(user)
        db.commit()
        db.refresh(user)
        return templates.TemplateResponse("verification.html", {"request": request, "username": user.username})
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"}
    )


 
@app.post('/token')
async def generate_token(request_form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    token = await authentication.token_generator(request_form.username, request_form.password, db)
    return {"access_token": token, "token_type": "bearer"}




@app.post('/user/me')
async def user_login(user: schemas.UserOut = Depends(get_current_user), db: Session = Depends(get_db)):
  
    business = db.query(models.Business).filter(models.Business.owner_id == user.id).first()
    
    logo = business.logo
    logo = "localhost:8000/static/images/"+logo

    return {"status" : "ok", 
            "data" : 
                {
                    "username" : user.username,
                    "email" : user.email,
                    "verified" : user.is_verified,
                    "join_date" : user.join_date.strftime("%b %d %Y"),
                    "logo" : logo
                }
            }





# image upload
@app.post("/uploadfile/profile")
async def create_upload_file(file: UploadFile = File(...),
                              user: schemas.UserOut = Depends(get_current_user), 
                              db: Session = Depends(get_db)):
    
    FILEPATH = "./static/images/"
    filename = file.filename
    extension = filename.split(".")[1]

    if extension not in ["jpg", "png"]:
        return {"status" : "error", "detail" : "file extension not allowed"}

    token_name = secrets.token_hex(10)+"."+extension
    generated_name = FILEPATH + token_name
    file_content = await file.read()
    with open(generated_name, "wb") as file:
        file.write(file_content)


    # pillow
    img = Image.open(generated_name)
    img = img.resize(size = (200,200))
    img.save(generated_name)

    file.close()
    
    business = db.query(models.Business).filter(models.Business.owner_id == user.id).first()
    owner = db.query(models.User).filter(models.User.id == user.id).first()
 
    
    if owner is not None:
        business.logo = token_name

        db.add(business)      # Optional, but safe if business was queried in this session
        db.commit()           # Commit the change to the database
        db.refresh(business)  # Refresh the instance with new data from DB


    else:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            detail = "Not authenticated to perform this action",
            headers={"WWW-Authenticate": "Bearer"},
        )
    file_url = "localhost:8000" + generated_name[1:]
    return {"status": "ok", "filename": file_url}




@app.post("/uploadfile/product/{id}")
async def create_upload_file(id: int, 
                             file: UploadFile = File(...), 
                             user: schemas.UserOut = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    
    FILEPATH = "./static/images/"
    filename = file.filename
    extension = filename.split(".")[1]
        
    if extension not in ["jpg", "png"]:
        return {"status" : "error", "detail" : "file extension not allowed"}

    token_name = secrets.token_hex(10)+"."+extension
    generated_name = FILEPATH + token_name
    file_content = await file.read()
    with open(generated_name, "wb") as file:
        file.write(file_content)

    # pillow
    img = Image.open(generated_name)
    img = img.resize(size = (200,200))
    img.save(generated_name)

    file.close()

    product = db.query(models.Product).filter(models.Product.id == id).first()
    business = db.query(models.Business).filter(models.Business.owner_id == user.id).first()
    owner = db.query(models.User).filter(models.User.id == user.id).first()

    if owner is not None:
        product.product_image = token_name

        db.add(product)      # Optional, but safe if product was queried in this session
        db.commit()           # Commit the change to the database
        db.refresh(product)

    else:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            detail = "Not authenticated to perform this action",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    file_url = "localhost:8000" + generated_name[1:]
    return {"status": "ok", "filename": file_url}













@app.post("/products")
async def add_new_product(
    product: schemas.ProductIn, 
    user: schemas.UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Calculate percentage discount
    product_data = product.dict()
    if product_data['original_price'] > 0:
        product_data["percentage_discount"] = (
            (product_data["original_price"] - product_data['new_price']) / product_data['original_price']
        ) * 100

    # Link product to business
    business = db.query(models.Business).filter(models.Business.owner_id == user.id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found for user")

    new_product = models.Product(**product_data, business_id=business.id)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return {"status": "ok", "data": jsonable_encoder(new_product)}


@app.get("/products")
async def get_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return {"status": "ok", "data": [jsonable_encoder(product) for product in products]}


@app.get("/products/{id}")
async def specific_product(id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    business = db.query(models.Business).filter(models.Business.id == product.business_id).first()
    owner = db.query(models.User).filter(models.User.id == business.owner_id).first()
    return {
        "status": "ok",
        "data": {
            "product_details": jsonable_encoder(product),
            "business_details": {
                "name": business.business_name,
                "city": business.city,
                "region": business.region,
                "description": business.business_description,
                "logo": business.logo,
                "owner_id": owner.id,
                "email": owner.email,
                "join_date": owner.join_date.strftime("%b %d %Y")
            }
        }
    }


@app.delete("/products/{id}")
async def delete_product(id: int, user: schemas.UserOut = Depends(get_current_user), db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    business = db.query(models.Business).filter(models.Business.id == product.business_id).first()
    owner = db.query(models.User).filter(models.User.id == business.owner_id).first()
    if user.id == owner.id:
        db.delete(product)
        db.commit()
        return {"status": "ok"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Not authenticated to perform this action",
            headers={"WWW-Authenticate": "Bearer"},
        )
