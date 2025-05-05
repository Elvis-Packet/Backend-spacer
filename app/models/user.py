from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, String, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel, db

class UserRole(enum.Enum):
    ADMIN = "admin"
    SPACE_OWNER = "space_owner"
    CLIENT = "client"

class User(BaseModel):
    """User model for authentication and authorization"""
    __tablename__ = 'users'

    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(100), nullable=True)
    profile_picture = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=True)

    # Relationships
    spaces = relationship('Space', backref='owner', lazy=True)
    bookings = relationship('Booking', backref='client', lazy=True)

    def __init__(self, email, password, first_name, last_name, role):
        self.email = email
        self.set_password(password)
        self.first_name = first_name
        self.last_name = last_name
        self.role = role

    def set_password(self, password):
        """Set the password hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role.value,
            'is_verified': self.is_verified,
            'profile_picture': self.profile_picture,
            'phone_number': self.phone_number,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 