from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from models.extensions import db, bcrypt, login_manager
from datetime import timedelta
from dotenv import load_dotenv
import os
from models.mate import User
from routes import auth_bp, english_bp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
load_dotenv(os.path.join(ROOT_DIR, '.env'))
load_dotenv(os.path.join(BASE_DIR, '.env'))


def configure_app(app):
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'SQLALCHEMY_DATABASE_URI', 'sqlite:///site.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = (
        os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False') == 'True'
    )
    app.config['TELEGRAM_BOT_TOKEN'] = os.getenv('TELEGRAM_BOT_TOKEN', '')
    app.config['TELEGRAM_CHAT_IDS'] = os.getenv('TELEGRAM_CHAT_IDS', '')
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=3)

    # Correct scheme/host when running behind nginx
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    if os.getenv('FLASK_ENV') == 'production':
        app.config['SESSION_COOKIE_SECURE'] = True
        app.config['REMEMBER_COOKIE_SECURE'] = True
        app.config['SESSION_COOKIE_HTTPONLY'] = True
        app.config['PREFERRED_URL_SCHEME'] = 'https'


def create_app():
    app = Flask(__name__)
    configure_app(app)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please sign in to continue.'
    login_manager.login_message_category = 'warning'

    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(english_bp, url_prefix='/')

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    return app


app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=os.getenv('FLASK_ENV') != 'production')
