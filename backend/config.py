import os

# Define the Upload Folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')  # Creates 'uploads' in the project directory


# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

class Config:
    OPENAI_API_KEY=os.environ.get('OPENAI_API_KEY')
    FIREFLIES_API_KEY=os.environ.get('FIREFLIES_API_KEY')
    SECRET_KEY = os.environ.get('SECRET_KEY','secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = UPLOAD_FOLDER

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL','postgresql://postgres:tony6666@localhost:5432/meeting_assistant')
    FRONTEND_URL = os.environ.get('FRONTEND_URL')  # Default to dev URL

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://dbmasteruser:Hm%263%25wY%2BnUO%26UPP%26V%7Br%7D%3A%25RRO%7Eigys%3Ak@ls-d66918d77233b573cb396a4f29f502640232d299.chwssi08mzyk.ca-central-1.rds.amazonaws.com:5432/meeting_assitant')
    FRONTEND_URL = os.environ.get('FRONTEND_URL')  # Default to dev URL

# Dictionary to easily switch configurations
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
