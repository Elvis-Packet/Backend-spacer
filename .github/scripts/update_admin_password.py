import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from config import Config
from app.models.base import db, init_db
from app.models.user import User, UserRole

def update_admin_password():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_db(app)

    with app.app_context():
        admin_email = 'admin@spacer.com'
        new_password = 'newadminpassword'  # Change this to your desired password

        admin_user = User.query.filter_by(email=admin_email).first()
        if not admin_user:
            print(f"No admin user found with email {admin_email}")
            return

        admin_user.set_password(new_password)
        db.session.commit()
        print(f"Password updated successfully for admin user {admin_email}")

if __name__ == '__main__':
    update_admin_password()
