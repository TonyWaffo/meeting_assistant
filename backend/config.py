import os

# Define the Upload Folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')  # Creates 'uploads' in the project directory


# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

class Config:
    OPENAI_API_KEY=os.environ.get('OPENAI_API_KEY', 'you-will-never-guess')
    FIREFLIES_API_KEY=os.environ.get('FIREFLIES_API_KEY', 'you-will-never-guess')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'you-will-never-guess')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = UPLOAD_FOLDER

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:tony6666@localhost:5432/meeting_assistant')
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')  # Default to dev URL

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://prod_user:prod_password@localhost/prod_db')
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')  # Default to dev URL

# Dictionary to easily switch configurations
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
