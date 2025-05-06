import os
import sys
from dotenv import load_dotenv

# Add project root to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from app.models.base import db, init_db
from app.models.user import User, UserRole

def create_admin_user():
    load_dotenv()  # Load environment variables from .env

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    init_db(app)

    with app.app_context():
        # Check if admin user already exists
        admin_email = "admin@example.com"
        existing_admin = User.query.filter_by(email=admin_email).first()
        if existing_admin:
            print(f"Admin user with email {admin_email} already exists.")
            return

        # Create new admin user
        admin_user = User(
            email=admin_email,
            password="adminpassword",
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN
        )
        db.session.add(admin_user)
        db.session.commit()
        print(f"Admin user created with email: {admin_email} and password: adminpassword")

if __name__ == "__main__":
    create_admin_user()
