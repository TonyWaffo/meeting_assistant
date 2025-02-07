import os
from dotenv import load_dotenv
from app import create_app

load_dotenv()  # Load environment variables from .env file

app = create_app()

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV', 'development') == 'development'
    app.run(debug=debug_mode, port=5000)
