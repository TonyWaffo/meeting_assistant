import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config

db = SQLAlchemy()
login = LoginManager()
migrate = Migrate()

def create_app():
    env = os.getenv('FLASK_ENV', 'development')  # Default to development
    app = Flask(__name__)
    app.config.from_object(config[env])  # Load the appropriate config

    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
