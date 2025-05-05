from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.testimonial import Testimonial
from ..models.user import User
from ..utils.auth import require_role
from ..models.base import db

testimonials_bp = Blueprint('testimonials', __name__)

@testimonials_bp.route('/', methods=['GET'])
def get_testimonials():
    """Get all approved testimonials"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    space_id = request.args.get('space_id', type=int)
    
    query = Testimonial.query.filter_by(status='approved')
    if space_id:
        query = query.filter_by(space_id=space_id)
    
    testimonials = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'testimonials': [testimonial.to_dict() for testimonial in testimonials.items],
        'total': testimonials.total,
        'pages': testimonials.pages,
        'current_page': testimonials.page
    }), 200

@testimonials_bp.route('/', methods=['POST'])
@jwt_required()
def create_testimonial():
    """Create a new testimonial"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['space_id', 'rating', 'comment']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Create new testimonial
    testimonial = Testimonial(
        user_id=current_user_id,
        space_id=data['space_id'],
        rating=data['rating'],
        comment=data['comment']
    )
    
    testimonial.save()
    
    return jsonify(testimonial.to_dict()), 201

@testimonials_bp.route('/<int:testimonial_id>', methods=['PUT'])
@jwt_required()
@require_role('admin')
def update_testimonial(testimonial_id):
    """Update testimonial status (admin only)"""
    testimonial = Testimonial.get_by_id(testimonial_id)
    if not testimonial:
        return jsonify({'message': 'Testimonial not found'}), 404
    
    data = request.get_json()
    if 'status' in data:
        testimonial.status = data['status']
    
    testimonial.save()
    
    return jsonify(testimonial.to_dict()), 200 