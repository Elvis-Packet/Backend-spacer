from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def hello():
        api_key = os.environ.get('APIKEY')
        return f"Hello, Flask app is running! Your API key is: {api_key}"

    return app
