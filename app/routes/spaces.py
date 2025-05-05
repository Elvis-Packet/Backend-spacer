from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.space import Space, SpaceType, SpaceStatus
from ..models.user import User, UserRole
from ..utils.cloudinary import upload_image, delete_image
from ..utils.auth import require_role
from ..models.base import db
import json

spaces_bp = Blueprint('spaces', __name__)

@spaces_bp.route('/', methods=['GET'])
def list_spaces():
    """Get all available spaces with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    space_type = request.args.get('type')
    city = request.args.get('city')
    
    query = Space.query.filter_by(is_active=True)
    
    if space_type:
        try:
            space_type_enum = SpaceType(space_type)
            query = query.filter_by(type=space_type_enum)
        except ValueError:
            return jsonify({'message': 'Invalid space type'}), 400
    
    if city:
        query = query.filter_by(city=city)
    
    spaces = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'spaces': [space.to_dict() for space in spaces.items],
        'total': spaces.total,
        'pages': spaces.pages,
        'current_page': spaces.page
    }), 200

@spaces_bp.route('/<int:space_id>', methods=['GET'])
def get_space_by_id(space_id):
    """Get a specific space by ID"""
    space = Space.get_by_id(space_id)
    if not space or not space.is_active:
        return jsonify({'message': 'Space not found'}), 404
    
    return jsonify(space.to_dict()), 200

@spaces_bp.route('/', methods=['POST'])
@jwt_required()
@require_role('space_owner')
def create_new_space():
    """Create a new space"""
    current_user_id = get_jwt_identity()
    data = request.form.to_dict()
    
    # Validate required fields
    required_fields = ['name', 'description', 'address', 'city', 'state', 
                      'country', 'postal_code', 'type', 'capacity', 
                      'price_per_hour', 'price_per_day']
    
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    try:
        space_type = SpaceType(data['type'])
    except ValueError:
        return jsonify({'message': 'Invalid space type'}), 400
    
    # Handle images
    images = []
    if 'images' in request.files:
        for image in request.files.getlist('images'):
            result = upload_image(image.read())
            if result:
                images.append(result['url'])
    
    # Create new space
    space = Space(
        name=data['name'],
        description=data['description'],
        address=data['address'],
        city=data['city'],
        state=data['state'],
        country=data['country'],
        postal_code=data['postal_code'],
        type=space_type,
        capacity=int(data['capacity']),
        price_per_hour=float(data['price_per_hour']),
        price_per_day=float(data['price_per_day']),
        images=json.dumps(images),
        amenities=data.get('amenities', '[]'),
        rules=data.get('rules', ''),
        owner_id=current_user_id
    )
    
    space.save()
    
    return jsonify(space.to_dict()), 201

@spaces_bp.route('/<int:space_id>', methods=['PUT'])
@jwt_required()
@require_role('space_owner')
def update_space_by_id(space_id):
    """Update a space"""
    current_user_id = get_jwt_identity()
    space = Space.get_by_id(space_id)
    
    if not space:
        return jsonify({'message': 'Space not found'}), 404
    
    if space.owner_id != current_user_id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    data = request.form.to_dict()
    
    # Update fields
    for field in ['name', 'description', 'address', 'city', 'state', 
                 'country', 'postal_code', 'capacity', 'price_per_hour', 
                 'price_per_day', 'amenities', 'rules']:
        if field in data:
            setattr(space, field, data[field])
    
    # Handle space type
    if 'type' in data:
        try:
            space.type = SpaceType(data['type'])
        except ValueError:
            return jsonify({'message': 'Invalid space type'}), 400
    
    # Handle images
    if 'images' in request.files:
        images = []
        for image in request.files.getlist('images'):
            result = upload_image(image.read())
            if result:
                images.append(result['url'])
        space.images = json.dumps(images)
    
    space.save()
    
    return jsonify(space.to_dict()), 200

@spaces_bp.route('/<int:space_id>', methods=['DELETE'])
@jwt_required()
@require_role('space_owner')
def delete_space_by_id(space_id):
    """Delete a space"""
    current_user_id = get_jwt_identity()
    space = Space.get_by_id(space_id)
    
    if not space:
        return jsonify({'message': 'Space not found'}), 404
    
    if space.owner_id != current_user_id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    space.is_active = False
    space.save()
    
    return jsonify({'message': 'Space deleted successfully'}), 200 