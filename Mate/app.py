from flask import Flask
from extensions import db, bcrypt, login_manager
from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS') == 'True'

app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=3)
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"
login_manager.login_message = "please-login"

from models import User
from routes import auth_bp

app.register_blueprint(auth_bp, url_prefix='/')

# User loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=5002, debug=False)

