from sqlalchemy import Column, String, Float, Integer, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel, db
from datetime import datetime

class SpaceType(enum.Enum):
    MEETING_ROOM = "meeting_room"
    EVENT_SPACE = "event_space"
    COWORKING = "coworking"
    STUDIO = "studio"
    OTHER = "other"

class SpaceStatus(enum.Enum):
    AVAILABLE = "available"
    BOOKED = "booked"
    MAINTENANCE = "maintenance"

class SpaceImage(db.Model):
    __tablename__ = 'space_images'
    
    id = db.Column(db.Integer, primary_key=True)
    space_id = db.Column(db.Integer, db.ForeignKey('spaces.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    public_id = db.Column(db.String(255), nullable=True)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    space = db.relationship('Space', back_populates='space_images')

class Space(BaseModel):
    """Space model for managing spaces in the platform"""
    __tablename__ = 'spaces'

    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    type = Column(Enum(SpaceType), nullable=False)
    status = Column(Enum(SpaceStatus), default=SpaceStatus.AVAILABLE)
    capacity = Column(Integer, nullable=False)
    price_per_hour = Column(Float, nullable=False)
    price_per_day = Column(Float, nullable=False)
    images = Column(Text, nullable=True)  # JSON string of image URLs

    def to_dict(self):
        """Convert space object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'type': self.type.value,
            'status': self.status.value,
            'capacity': self.capacity,
            'price_per_hour': self.price_per_hour,
            'price_per_day': self.price_per_day,
            'images': [{
                'url': img.image_url,
                'is_primary': img.is_primary
            } for img in self.space_images],
            'amenities': self.amenities,
            'rules': self.rules,
            'owner_id': self.owner_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    amenities = Column(Text, nullable=True)  # JSON string of amenities
    rules = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    bookings = relationship('Booking', backref='space', lazy=True)
    space_images = relationship('SpaceImage', back_populates='space', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        """Convert space object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'type': self.type.value,
            'status': self.status.value,
            'capacity': self.capacity,
            'price_per_hour': self.price_per_hour,
            'price_per_day': self.price_per_day,
            'images': self.images,
            'amenities': self.amenities,
            'rules': self.rules,
            'owner_id': self.owner_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'images': [{
                'id': img.id,
                'url': img.image_url,
                'is_primary': img.is_primary
            } for img in self.space_images]
        }

    def add_image(self, image_url, public_id, is_primary=False):
        """Add an image to the space"""
        # If this is the first image or is_primary is True, set it as primary
        if is_primary or not self.space_images:
            # Unset any existing primary image
            for img in self.space_images:
                img.is_primary = False
            is_primary = True
        
        image = SpaceImage(
            space_id=self.id,
            image_url=image_url,
            public_id=public_id,
            is_primary=is_primary
        )
        db.session.add(image)
        return image
    
    def remove_image(self, image_id):
        """Remove an image from the space"""
        image = SpaceImage.query.get(image_id)
        if image and image.space_id == self.id:
            db.session.delete(image)
            # If this was the primary image, set another image as primary
            if image.is_primary and self.space_images:
                self.space_images[0].is_primary = True
            return True
        return False
    
    def set_primary_image(self, image_id):
        """Set an image as the primary image"""
        image = SpaceImage.query.get(image_id)
        if image and image.space_id == self.id:
            # Unset current primary image
            for img in self.space_images:
                img.is_primary = False
            # Set new primary image
            image.is_primary = True
            return True
        return False 