import os
import motor.motor_asyncio
import databases

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv


load_dotenv()


DATABASE_URL = os.getenv('DATABASE_URL')

database = databases.Database(DATABASE_URL)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

db = SessionLocal()

mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
    host=os.getenv('HOST'), port=27017)

DB = 'clubs'
