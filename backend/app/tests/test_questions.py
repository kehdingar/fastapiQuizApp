from app.schemas.user import UserCreate
from app.api.auth import get_db, get_user
from app.main import app
from sqlmodel import SQLModel
from sqlalchemy import create_engine,StaticPool
from sqlalchemy.orm import sessionmaker
from app.models import *
from app.models.user import Role, User
from app.api.auth import get_password_hash
from app.api.auth import verify_password



SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    # This will make sure we don't get inconsistencies while writing tests. Tha's how sqlite works and we have to deal with it
    connect_args={
        "check_same_thread":False,
    },
    # We make sure its a static connection pool so that we connect to the same memory database
    # This will allow us to create something in our database and later read it
    poolclass=StaticPool,
    )

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def setup():
    with TestingSessionLocal() as session:
        # Create necessary tables for each test case
        SQLModel.metadata.create_all(bind=session.get_bind())

        # Create Instructor user at the beninning of the test

        instructor_data = {
            "email":'firstInstructorTest@quiz.com', 
            "password":get_password_hash('firstInsructorTestPassword'),
            "role" :Role.INSTRUCTOR,
            }
        instructor_db_user = User(email=instructor_data['email'],password=instructor_data['password'],role=instructor_data['role'])

        # Create a user at the beginning of the test
        user_data = UserCreate(email='firstTest@quiz.com', password=get_password_hash('firstTestPassword'))
        db_user = User(**user_data.model_dump())
        session.add(db_user)
        session.add(instructor_db_user)
        session.commit()
        session.refresh(db_user)
        session.refresh(instructor_db_user)


def tearDown():
    SQLModel.metadata.drop_all(bind=engine)


def test_initial_test_user():
    db = TestingSessionLocal()
    user = get_user(db=db, email="firstTest@quiz.com")
    hash_password = get_password_hash("firstTestPassword")
    assert user.email =="firstTest@quiz.com"
    assert True == verify_password("firstTestPassword",hash_password)
    assert user.role =="Student"


def test_initial_test_instructor_user():
    db = TestingSessionLocal()
    user = get_user(db=db, email="firstInstructorTest@quiz.com")
    hash_password = get_password_hash("firstTestPassword")
    print(f"\n user role {user.role}")
    assert user.email =="firstInstructorTest@quiz.com"
    assert True == verify_password("firstTestPassword",hash_password)
    assert user.role =="Instructor"