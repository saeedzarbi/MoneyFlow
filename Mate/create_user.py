from app import create_app
from models.extensions import bcrypt, db
from models.mate import User

def create_user(email, password, username):
    app = create_app()
    with app.app_context():
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            print("User with this email already exists!")
            return
        
        # Create new user
        user = User(
            username=username,
            email=email
        )
        user.set_password(password)
        
        # Add to database
        db.session.add(user)
        db.session.commit()
        print("User created successfully!")

if __name__ == "__main__":
    # Example usage
    create_user("test@example.com", "password123", "testuser") 