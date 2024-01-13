from app.models.user import User,Role
from app.api.utils.database import get_db


def update_user_role(user, db):
    # Check if user is already an instructor
    if user.role == Role.INSTRUCTOR:
        print("User is already an instructor.")
        return

    # Update user role to instructor
    user.role = Role.INSTRUCTOR
    db.commit()
    print("User role updated to instructor.")

if __name__ == "__main__":
    email = input("Enter email: ")

    db = next(get_db())

    # Check if user exists
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print("User not found.")
    else:
        update_user_role(user, db)