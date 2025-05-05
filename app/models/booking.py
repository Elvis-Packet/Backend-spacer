from sqlalchemy import Column, Integer, Float, DateTime, Enum, ForeignKey, Text, Boolean, String
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel, db

class BookingStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class Booking(BaseModel):
    """Booking model for managing space bookings"""
    __tablename__ = 'bookings'

    space_id = Column(Integer, ForeignKey('spaces.id'), nullable=False)
    client_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    total_amount = Column(Float, nullable=False)
    payment_status = Column(Boolean, default=False)
    payment_reference = Column(String(100), nullable=True)
    special_requests = Column(Text, nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    def calculate_total_amount(self, space):
        """Calculate the total amount for the booking"""
        duration_hours = (self.end_time - self.start_time).total_seconds() / 3600
        if duration_hours <= 24:
            return duration_hours * space.price_per_hour
        else:
            days = duration_hours / 24
            return days * space.price_per_day

    def to_dict(self):
        """Convert booking object to dictionary"""
        return {
            'id': self.id,
            'space_id': self.space_id,
            'client_id': self.client_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'status': self.status.value,
            'total_amount': self.total_amount,
            'payment_status': self.payment_status,
            'payment_reference': self.payment_reference,
            'special_requests': self.special_requests,
            'cancellation_reason': self.cancellation_reason,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 