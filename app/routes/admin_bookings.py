from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.booking import Booking, BookingStatus
from app.models.space import Space, SpaceStatus
from app.models.user import User, UserRole
from app.utils.auth import require_role
from app.models.base import db

admin_bookings_bp = Blueprint('admin_bookings', __name__, url_prefix='/admin/bookings')

@admin_bookings_bp.route('/', methods=['GET'])
@jwt_required()
@require_role('admin')
def get_bookings():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status_filter = request.args.get('status')

    query = Booking.query
    if status_filter:
        try:
            status_enum = BookingStatus(status_filter)
            query = query.filter(Booking.status == status_enum)
        except ValueError:
            return jsonify({'error': 'Invalid status filter'}), 400

    pagination = query.paginate(page=page, per_page=per_page)
    bookings = []
    for booking in pagination.items:
        b = booking.to_dict()
        # Add related space and user info
        b['space'] = booking.space.to_dict() if booking.space else None
        b['user'] = booking.client.to_dict() if booking.client else None
        bookings.append(b)

    return jsonify({
        'bookings': bookings,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    }), 200

@admin_bookings_bp.route('/<int:booking_id>', methods=['PUT'])
@jwt_required()
@require_role('admin')
def update_booking(booking_id):
    data = request.get_json()
    status = data.get('status')
    if not status:
        return jsonify({'error': 'Status is required'}), 400

    try:
        status_enum = BookingStatus(status)
    except ValueError:
        return jsonify({'error': 'Invalid status value'}), 400

    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    booking.status = status_enum

    # Update space status accordingly
    if status_enum == BookingStatus.CONFIRMED:
        booking.space.status = SpaceStatus.BOOKED
    elif status_enum in [BookingStatus.CANCELLED, BookingStatus.COMPLETED]:
        booking.space.status = SpaceStatus.AVAILABLE

    try:
        db.session.commit()
        return jsonify({'message': 'Booking updated successfully', 'booking': booking.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
