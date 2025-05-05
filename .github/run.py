from app import create_app
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = create_app()

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', '1') == '1') 