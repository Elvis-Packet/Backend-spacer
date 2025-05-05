from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.user import User, UserRole
from ..models.space import Space
from ..models.booking import Booking, BookingStatus
from ..models.testimonial import Testimonial
from ..utils.auth import require_role
from ..models.base import db
from datetime import datetime, timedelta
import json

admin_bp = Blueprint('admin', __name__)

# User Management
@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@require_role('admin')
def get_users():
    """Get all users with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    role = request.args.get('role')
    
    query = User.query
    
    if role:
        try:
            role_enum = UserRole(role)
            query = query.filter_by(role=role_enum)
        except ValueError:
            return jsonify({'message': 'Invalid role'}), 400
    
    users = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'users': [user.to_dict() for user in users.items],
        'total': users.total,
        'pages': users.pages,
        'current_page': users.page
    }), 200

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
@require_role('admin')
def get_user(user_id):
    """Get a specific user"""
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@require_role('admin')
def update_user(user_id):
    """Update a user's details"""
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update fields
    for field in ['first_name', 'last_name', 'email', 'role']:
        if field in data:
            if field == 'role':
                try:
                    setattr(user, field, UserRole(data[field]))
                except ValueError:
                    return jsonify({'message': 'Invalid role'}), 400
            else:
                setattr(user, field, data[field])
    
    user.save()
    return jsonify(user.to_dict()), 200

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@require_role('admin')
def delete_user(user_id):
    """Delete a user"""
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    user.is_active = False
    user.save()
    return jsonify({'message': 'User deleted successfully'}), 200

# Space Management
@admin_bp.route('/spaces', methods=['GET'])
@jwt_required()
@require_role('admin')
def get_all_spaces():
    """Get all spaces with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    
    query = Space.query
    
    if status:
        try:
            status_enum = SpaceStatus(status)
            query = query.filter_by(status=status_enum)
        except ValueError:
            return jsonify({'message': 'Invalid status'}), 400
    
    spaces = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'spaces': [space.to_dict() for space in spaces.items],
        'total': spaces.total,
        'pages': spaces.pages,
        'current_page': spaces.page
    }), 200

@admin_bp.route('/spaces/<int:space_id>', methods=['PUT'])
@jwt_required()
@require_role('admin')
def update_space(space_id):
    """Update any space"""
    space = Space.get_by_id(space_id)
    if not space:
        return jsonify({'message': 'Space not found'}), 404
    
    data = request.get_json()
    
    # Update fields
    for field in ['name', 'description', 'address', 'city', 'state', 
                 'country', 'postal_code', 'type', 'capacity', 
                 'price_per_hour', 'price_per_day', 'status']:
        if field in data:
            if field == 'type':
                try:
                    setattr(space, field, SpaceType(data[field]))
                except ValueError:
                    return jsonify({'message': 'Invalid space type'}), 400
            elif field == 'status':
                try:
                    setattr(space, field, SpaceStatus(data[field]))
                except ValueError:
                    return jsonify({'message': 'Invalid status'}), 400
            else:
                setattr(space, field, data[field])
    
    space.save()
    return jsonify(space.to_dict()), 200

# Booking Management
@admin_bp.route('/bookings', methods=['GET'])
@jwt_required()
@require_role('admin')
def get_all_bookings():
    """Get all bookings with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    
    query = Booking.query
    
    if status:
        try:
            status_enum = BookingStatus(status)
            query = query.filter_by(status=status_enum)
        except ValueError:
            return jsonify({'message': 'Invalid status'}), 400
    
    bookings = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'bookings': [booking.to_dict() for booking in bookings.items],
        'total': bookings.total,
        'pages': bookings.pages,
        'current_page': bookings.page
    }), 200

@admin_bp.route('/bookings/<int:booking_id>', methods=['PUT'])
@jwt_required()
@require_role('admin')
def update_booking(booking_id):
    """Update booking status"""
    booking = Booking.get_by_id(booking_id)
    if not booking:
        return jsonify({'message': 'Booking not found'}), 404
    
    data = request.get_json()
    if 'status' in data:
        try:
            booking.status = BookingStatus(data['status'])
            booking.save()
            return jsonify(booking.to_dict()), 200
        except ValueError:
            return jsonify({'message': 'Invalid status'}), 400
    
    return jsonify({'message': 'No status provided'}), 400

# Testimonial Management
@admin_bp.route('/testimonials', methods=['GET'])
@jwt_required()
@require_role('admin')
def get_all_testimonials():
    """Get all testimonials with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    
    query = Testimonial.query
    
    if status:
        query = query.filter_by(status=status)
    
    testimonials = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'testimonials': [testimonial.to_dict() for testimonial in testimonials.items],
        'total': testimonials.total,
        'pages': testimonials.pages,
        'current_page': testimonials.page
    }), 200

@admin_bp.route('/testimonials/<int:testimonial_id>', methods=['PUT'])
@jwt_required()
@require_role('admin')
def update_testimonial(testimonial_id):
    """Update testimonial status"""
    testimonial = Testimonial.get_by_id(testimonial_id)
    if not testimonial:
        return jsonify({'message': 'Testimonial not found'}), 404
    
    data = request.get_json()
    if 'status' in data:
        testimonial.status = data['status']
        testimonial.save()
        return jsonify(testimonial.to_dict()), 200
    
    return jsonify({'message': 'No status provided'}), 400

# Platform Statistics
@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
@require_role('admin')
def get_stats():
    """Get platform statistics"""
    total_users = User.query.count()
    total_spaces = Space.query.count()
    total_bookings = Booking.query.count()
    active_bookings = Booking.query.filter_by(status=BookingStatus.CONFIRMED).count()
    
    # Calculate revenue for the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_bookings = Booking.query.filter(
        Booking.created_at >= thirty_days_ago,
        Booking.status == BookingStatus.CONFIRMED
    ).all()
    
    total_revenue = sum(booking.total_amount for booking in recent_bookings)
    
    return jsonify({
        'total_users': total_users,
        'total_spaces': total_spaces,
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'revenue_last_30_days': total_revenue
    }), 200 