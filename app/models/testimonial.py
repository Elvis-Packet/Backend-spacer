from sqlalchemy import Column, String, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from .base import BaseModel, db

class Testimonial(BaseModel):
    """Testimonial model for user reviews"""
    __tablename__ = 'testimonials'

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    space_id = Column(Integer, ForeignKey('spaces.id'), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=False)
    status = Column(String(20), default='pending')  # pending, approved, rejected

    # Relationships
    user = relationship('User', backref='testimonials')
    space = relationship('Space', backref='testimonials')

    def to_dict(self):
        """Convert testimonial object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'space_id': self.space_id,
            'rating': self.rating,
            'comment': self.comment,
            'status': self.status,
            'user': {
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'profile_picture': self.user.profile_picture
            },
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 