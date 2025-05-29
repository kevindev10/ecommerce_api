from fastapi import FastAPI
import os
import models, schemas
from database import engine
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

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