from getpass import getpass
from datetime import datetime
from app.models.user import User,Role
from app.api.utils.database import get_db
import make_instructor
from app.api.auth import get_password_hash


def create_instructor():
    email = input("Enter email: ")
    password = getpass("Enter password: ")
    password = get_password_hash(password)

    # generator object is an iterable that can produce values on demand, 
    # but it does not have the methods of a session object, such as query, add, or commit. 
    # To get a session object from a generator, you need to use the next function
    db = next(get_db())

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        if existing_user.is_superuser:
            print("User already exists as a instructor.")
        else:
            make_instructor.update_user_role(existing_user, db)
        return

    # Create superuser
    superuser = User(
        email=email,
        password=password,
        role=Role.INSTRUCTOR,
        is_superuser=True,
        created_at=datetime.now(),
        modified_at=datetime.now()
    )

    db.add(superuser)
    db.commit()
    print("Instrutor created successfully.")

if __name__ == "__main__":
    create_instructor()