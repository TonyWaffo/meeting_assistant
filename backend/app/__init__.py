import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS  # Import CORS
from config import config
from dotenv import load_dotenv
import threading

db = SQLAlchemy()
login = LoginManager()
migrate = Migrate()

def create_app():
    load_dotenv()  # Load environment variables from .env file

    env = os.getenv('FLASK_ENV', 'development')  # Default to development
    app = Flask(__name__)
    app.config.from_object(config[env])  # Load the appropriate config

    # Get the frontend URL directly from the config
    frontend_url = app.config['FRONTEND_URL']  # Access from config

    # Set up CORS to allow requests from the frontend
    CORS(app, supports_credentials=True, origins="*", methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"])  # Use the frontend URL dynamically

    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)

    @app.route('/')  # Define route for "/"
    def home():
        return "Welcome to my Flask app!"

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    from app.audio_routes import bp as audio_bp,run_cleanup_periodically
    app.register_blueprint(audio_bp)

    # Start the cleanup thread with the application context
    def run_cleanup_with_context():
        with app.app_context():  # Push the application context
            run_cleanup_periodically()

    # Start the cleanup thread
    cleanup_thread = threading.Thread(target=run_cleanup_with_context, daemon=True)
    cleanup_thread.start()

    return app
