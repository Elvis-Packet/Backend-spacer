import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from config import Config
from app.models.base import db, init_db
from app.models import User, Space, SpaceImage, Booking, Testimonial
from app.models.user import UserRole
from app.models.space import SpaceType, SpaceStatus
from app.models.booking import BookingStatus
from datetime import datetime, timedelta
import json

def seed_database():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_db(app)
    
    with app.app_context():
        # Clear existing data
        db.session.query(Booking).delete()
        db.session.query(SpaceImage).delete()
        db.session.query(Space).delete()
        db.session.query(User).delete()
        db.session.commit()

        # Create users
        users = [
            User(
                email='admin@spacer.com',
                password='hashed_password',  # In production, use proper password hashing
                first_name='Admin',
                last_name='User',
                role=UserRole.ADMIN
            ),
            User(
                email='user@spacer.com',
                password='hashed_password',
                first_name='Regular',
                last_name='User',
                role=UserRole.CLIENT
            )
        ]
        for user in users:
            user.is_verified = True
        db.session.add_all(users)
        db.session.commit()

        # Create spaces
        spaces = [
            Space(
                name='Modern Downtown Office',
                description='A sleek, modern office space in the heart of downtown, perfect for meetings and collaborative work.',
                address='123 Main St',
                city='New York',
                state='NY',
                country='USA',
                postal_code='10001',
                type=SpaceType.MEETING_ROOM,
                status=SpaceStatus.AVAILABLE,
                capacity=12,
                price_per_hour=45,
                price_per_day=320,
                amenities=json.dumps([
                    'High-speed WiFi',
                    'Conference room',
                    'Kitchen',
                    'Projector',
                    'Whiteboards',
                    'Parking',
                    'Coffee/Tea',
                    'Air conditioning'
                ]),
                owner_id=1
            ),
            Space(
                name='Cozy Art Studio',
                description='A bright and spacious art studio with natural lighting, perfect for photography or artistic work.',
                address='456 Williamsburg Ave',
                city='Brooklyn',
                state='NY',
                country='USA',
                postal_code='11211',
                type=SpaceType.STUDIO,
                status=SpaceStatus.AVAILABLE,
                capacity=6,
                price_per_hour=35,
                price_per_day=250,
                amenities=json.dumps([
                    'Natural lighting',
                    'Storage space',
                    'Sink/water access',
                    'WiFi',
                    'Restroom',
                    'Climate control',
                    'Sound system'
                ]),
                owner_id=1
            )
        ]
        db.session.add_all(spaces)
        db.session.commit()

        # Create space images
        space_images = []
        for space in spaces:
            if space.name == 'Modern Downtown Office':
                images = [
                    'https://images.pexels.com/photos/1170412/pexels-photo-1170412.jpeg',
                    'https://images.pexels.com/photos/260931/pexels-photo-260931.jpeg',
                    'https://images.pexels.com/photos/380768/pexels-photo-380768.jpeg'
                ]
            else:
                images = [
                    'https://images.pexels.com/photos/6306387/pexels-photo-6306387.jpeg',
                    'https://images.pexels.com/photos/4039921/pexels-photo-4039921.jpeg',
                    'https://images.pexels.com/photos/5083407/pexels-photo-5083407.jpeg'
                ]
            
            for i, image_url in enumerate(images):
                space_images.append(SpaceImage(
                    space_id=space.id,
                    image_url=image_url,
                    is_primary=(i == 0)
                ))
        
        db.session.add_all(space_images)
        db.session.commit()

        # Create bookings
        bookings = [
            Booking(
                space_id=1,
                client_id=2,
                start_time=datetime.now() + timedelta(days=1),
                end_time=datetime.now() + timedelta(days=1, hours=4),
                status=BookingStatus.CONFIRMED,
                total_amount=180
            ),
            Booking(
                space_id=2,
                client_id=1,
                start_time=datetime.now() + timedelta(days=2),
                end_time=datetime.now() + timedelta(days=2, hours=4),
                status=BookingStatus.CONFIRMED,
                total_amount=140
            )
        ]
        db.session.add_all(bookings)
        db.session.commit()

        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database() 