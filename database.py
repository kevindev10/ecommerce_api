import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings
import psycopg2



db_password = settings.database_password
db_username = settings.database_username
db_name = settings.database_name
db_hostname = settings.database_hostname
db_port = settings.database_port



# SQLALCHEMY_DATABASE_URL = "postgresql://<username>:<password>@<ip-address/hostname>/<database_name>"

SQLALCHEMY_DATABASE_URL = f"postgresql://{db_username}:{db_password}@{db_hostname}:{db_port}/{db_name}"



# Create the SQLAlchemy engine to connect to any SQL database other than SQLite
engine = create_engine(SQLALCHEMY_DATABASE_URL)


# Create a sessionmaker object to create a session to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create a base class for our database models. All models we will be defining will inherit from this class/will be extending this class.
Base = declarative_base()


# Dependency. This function will create a new database session for each request and close it once the request is done. This will be passed as a parameter to the path operation functions that need to interact with the database.Meaning, the function will be called opening a session to our database and closing it once the request is done for each path operation.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

