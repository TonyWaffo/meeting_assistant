import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'you-will-never-guess')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL', 'postgresql://postgres:tony6666@localhost:5432/meeting_assistant')
    FRONTEND_URL = os.environ.get('DEV_FRONTEND_URL', 'http://localhost:3000')  # Default to dev URL

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://prod_user:prod_password@localhost/prod_db')
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')  # Default to dev URL

# Dictionary to easily switch configurations
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
