from flask import Flask
from models.extensions import db, bcrypt, login_manager
from datetime import timedelta
from dotenv import load_dotenv
import os
from models.mate import User
from routes import auth_bp, english_bp
from flask_wtf.csrf import CSRFProtect

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')  # Default secret key if not in .env
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False') == 'True'
app.config['SLACK-HOOK'] = os.getenv('SLACK-HOOK', 'False') == 'True'

app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=3)

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
csrf = CSRFProtect(app)

login_manager.login_view = "auth.login"
login_manager.login_message = "please-login"

app.register_blueprint(auth_bp, url_prefix='/')
app.register_blueprint(english_bp, url_prefix='/')

# User loader function
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///site.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf = CSRFProtect(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(english_bp, url_prefix='/')
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
            db.create_all()
    app.run(debug=True)

