# app.py
from flask import Flask
from extensions import db, bcrypt, login_manager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions with app
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)

# Import models and routes after initializing extensions to avoid circular imports
from models import User
from routes import auth_bp

app.register_blueprint(auth_bp, url_prefix='/auth')

# User loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
