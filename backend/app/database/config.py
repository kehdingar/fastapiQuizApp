from dotenv import load_dotenv,find_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

dotenv_path = find_dotenv(raise_error_if_not_found=True, usecwd=True)
load_dotenv(dotenv_path)


if os.getenv("TESTING"):
    SQLALCHEMY_DATABASE_URL = "sqlite:///test.db"
    # When about to start test for the first time, set the python environment varaible on commandline to be true like so
    # command: export TESTING=1
    # then run test
else:
    SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()