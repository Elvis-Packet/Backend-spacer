from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.space import Space, SpaceImage, SpaceType, SpaceStatus
from app.utils.image_handler import upload_image, delete_image, configure_cloudinary
from app.utils.auth import require_role
from app import db
from datetime import datetime
import os

bp = Blueprint('spaces', __name__)

def format_space(space):
    """Helper to format space dict with human-readable dates"""
    d = space.to_dict()
    d['created_at'] = space.created_at.strftime('%Y-%m-%d %H:%M:%S')
    d['updated_at'] = space.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    return d

@bp.route('/', methods=['POST'])
@jwt_required()
@require_role('space_owner')
def create_space():
    try:
        current_user_id = get_jwt_identity()
        data = request.form.to_dict()
        images = request.files.getlist('images')
        image_urls = request.form.get('image_urls')
        if image_urls:
            import json
            image_urls = json.loads(image_urls)
        else:
            image_urls = []

        # Remove image_urls and images fields from data to avoid passing invalid keyword arguments
        if 'image_urls' in data:
            del data['image_urls']
        if 'images' in data:
            del data['images']

        # Validate required fields
        required_fields = ['name', 'description', 'address', 'city', 'state', 'country', 'postal_code', 'type', 'capacity', 'price_per_hour', 'price_per_day']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Validate space type
        try:
            space_type = SpaceType(data['type'])
        except ValueError:
            return jsonify({'error': 'Invalid space type'}), 400

        import json
        # Convert amenities to JSON string if it's a list or dict
        amenities = data.get('amenities')
        if amenities and not isinstance(amenities, str):
            amenities = json.dumps(amenities)

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
            owner_id=current_user_id,
            status=SpaceStatus.AVAILABLE,
            is_active=True,
            amenities=amenities
        )
        db.session.add(space)
        db.session.flush()

        # Upload and add images from files
        for i, image in enumerate(images):
            result = upload_image(image)
            if result.get('success'):
                space.add_image(
                    image_url=result['url'],
                    public_id=result['public_id'],
                    is_primary=(i == 0)
                )
        # Add images from external URLs
        for i, url in enumerate(image_urls):
            space.add_image(
                image_url=url,
                public_id=None,
                is_primary=(i == 0 and not images)
            )

        db.session.commit()
        return jsonify({'message': 'Space created successfully', 'space': format_space(space)}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:space_id>', methods=['PUT'])
@jwt_required()
@require_role('space_owner')
def update_space(space_id):
    try:
        current_user_id = get_jwt_identity()
        space = Space.query.get_or_404(space_id)

        if space.owner_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        data = request.form.to_dict()
        new_images = request.files.getlist('images')
        image_urls = request.form.get('image_urls')
        if image_urls:
            import json
            image_urls = json.loads(image_urls)
        else:
            image_urls = []

        # Remove image_urls from data to avoid passing invalid keyword argument
        if 'image_urls' in data:
            del data['image_urls']

        # Update fields
        for key in ['name', 'description', 'address', 'city', 'state', 'country', 'postal_code', 'capacity', 'price_per_hour', 'price_per_day', 'status']:
            if key in data:
                if key == 'status':
                    try:
                        setattr(space, key, SpaceStatus(data[key]))
                    except ValueError:
                        return jsonify({'error': 'Invalid status value'}), 400
                else:
                    setattr(space, key, data[key])

        # Update type if provided
        if 'type' in data:
            try:
                space.type = SpaceType(data['type'])
            except ValueError:
                return jsonify({'error': 'Invalid space type'}), 400

        # Handle new images from files
        for image in new_images:
            result = upload_image(image)
            if result.get('success'):
                space.add_image(
                    image_url=result['url'],
                    public_id=result['public_id']
                )
        # Handle new images from external URLs
        for url in image_urls:
            space.add_image(
                image_url=url,
                public_id=None
            )

        # Handle image deletions
        deleted_image_ids = request.form.getlist('deleted_image_ids')
        for image_id in deleted_image_ids:
            image = SpaceImage.query.get(image_id)
            if image and image.space_id == space.id:
                delete_image(image.public_id)
                space.remove_image(image_id)

        # Handle primary image change
        primary_image_id = request.form.get('primary_image_id')
        if primary_image_id:
            space.set_primary_image(primary_image_id)

        db.session.commit()
        return jsonify({'message': 'Space updated successfully', 'space': format_space(space)}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:space_id>', methods=['DELETE'])
@jwt_required()
@require_role('space_owner')
def delete_space(space_id):
    try:
        current_user_id = get_jwt_identity()
        space = Space.query.get_or_404(space_id)

        if space.owner_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        # Soft delete
        space.is_active = False
        db.session.commit()
        return jsonify({'message': 'Space deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/', methods=['GET'])
def get_spaces():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        filters = {
            'type': request.args.get('type'),
            'city': request.args.get('city'),
            'status': request.args.get('status')
        }

        query = Space.query.filter_by(is_active=True)

        # Apply filters
        for key, value in filters.items():
            if value:
                if key == 'type':
                    try:
                        value = SpaceType(value)
                    except ValueError:
                        return jsonify({'error': 'Invalid space type filter'}), 400
                if key == 'status':
                    try:
                        value = SpaceStatus(value)
                    except ValueError:
                        return jsonify({'error': 'Invalid status filter'}), 400
                query = query.filter(getattr(Space, key) == value)

        pagination = query.paginate(page=page, per_page=per_page)
        spaces = [format_space(space) for space in pagination.items]

        return jsonify({
            'spaces': spaces,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/owner', methods=['GET'])
@jwt_required()
@require_role('space_owner')
def get_owner_spaces():
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        pagination = Space.query.filter_by(owner_id=current_user_id, is_active=True).paginate(page=page, per_page=per_page)
        spaces = [format_space(space) for space in pagination.items]

        return jsonify({
            'spaces': spaces,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
