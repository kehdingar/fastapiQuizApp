from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# from . config import Settings

if os.getenv("TESTING"):
    SQLALCHEMY_DATABASE_URL = "sqlite:///test.db"
else:
    SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@database:5432/quiz_db"
# SQLALCHEMY_DATABASE_URL = Settings().database_url

engine = create_engine(SQLALCHEMY_DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()