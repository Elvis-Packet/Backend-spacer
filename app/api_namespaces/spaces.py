from flask_restx import Namespace, Resource, fields, reqparse
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Space, User
from app.models.user import UserRole
from app.models.space import SpaceType, SpaceStatus
from app.models.base import db
from app.utils.cloudinary import upload_image
from werkzeug.datastructures import FileStorage

spaces_ns = Namespace('spaces', description='Space operations')

image_model = spaces_ns.model('SpaceImage', {
    'id': fields.Integer(readonly=True),
    'url': fields.String(required=True, description='URL of the image'),
    'is_primary': fields.Boolean(required=False, description='Set as primary image')
})

space_model = spaces_ns.model('Space', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(required=True),
    'description': fields.String(required=True),
    'address': fields.String(required=True),
    'city': fields.String(required=True),
    'state': fields.String(required=True),
    'country': fields.String(required=True),
    'postal_code': fields.String(required=True),
    'type': fields.String(required=True),
    'status': fields.String(required=True),
    'capacity': fields.Integer(required=True),
    'price_per_hour': fields.Float(required=True),
    'price_per_day': fields.Float(required=True),
    'amenities': fields.String,
    'owner_id': fields.Integer(required=True),
    'images': fields.List(fields.Nested(image_model))
})

image_upload_parser = reqparse.RequestParser()
image_upload_parser.add_argument('image', type=FileStorage, location='files', required=True, help='Image file')
image_upload_parser.add_argument('is_primary', type=bool, location='form', required=False, default=False)

@spaces_ns.route('/')
class SpaceList(Resource):
    def get(self):
        """Get all spaces with optional pagination and status filter"""
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        status = request.args.get('status', type=str)

        query = Space.query
        if status:
            try:
                query = query.filter(Space.status == SpaceStatus(status))
            except ValueError:
                return {'message': 'Invalid status filter'}, 400

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        spaces = pagination.items
        return [space.to_dict() for space in spaces]

    @jwt_required()
    @spaces_ns.expect(space_model)
    def post(self):
        """Create a new space"""
        data = request.get_json()
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if current_user.role not in [UserRole.SPACE_OWNER, UserRole.ADMIN]:
            return {'message': 'Unauthorized'}, 403
        if 'owner_id' in data:
            data.pop('owner_id')
        try:
            data['type'] = SpaceType(data['type'])
        except ValueError:
            return {'message': 'Invalid space type'}, 400
        if 'status' in data:
            try:
                data['status'] = SpaceStatus(data['status'])
            except ValueError:
                return {'message': 'Invalid space status'}, 400
        space = Space(owner_id=current_user_id, **data)
        space.save()
        return {'message': 'Space created successfully'}, 201

@spaces_ns.route('/<int:space_id>')
class SpaceDetail(Resource):
    def get(self, space_id):
        """Get space details"""
        return Space.query.get_or_404(space_id)

    @jwt_required()
    @spaces_ns.expect(space_model)
    def put(self, space_id):
        """Update space details"""
        space = Space.query.get_or_404(space_id)
        current_user_id = get_jwt_identity()
        if space.owner_id != current_user_id:
            return {'message': 'Unauthorized'}, 403
        data = request.get_json()
        if 'type' in data:
            try:
                data['type'] = SpaceType(data['type'])
            except ValueError:
                return {'message': 'Invalid space type'}, 400
        if 'status' in data:
            try:
                data['status'] = SpaceStatus(data['status'])
            except ValueError:
                return {'message': 'Invalid space status'}, 400
        for key, value in data.items():
            setattr(space, key, value)
        space.save()
        return {'message': 'Space updated successfully'}

    @jwt_required()
    def delete(self, space_id):
        """Delete a space"""
        space = Space.query.get_or_404(space_id)
        current_user_id = get_jwt_identity()
        if space.owner_id != current_user_id:
            return {'message': 'Unauthorized'}, 403
        space.delete()
        return {'message': 'Space deleted successfully'}

@spaces_ns.route('/<int:space_id>/images')
class SpaceImageList(Resource):
    @jwt_required()
    @spaces_ns.expect(image_upload_parser)
    def post(self, space_id):
        """Add an image to a space"""
        args = image_upload_parser.parse_args()
        image_file = args.get('image')
        is_primary = args.get('is_primary', False)
        if not image_file:
            return {'message': 'Image file is required'}, 400
        space = Space.query.get_or_404(space_id)
        current_user_id = get_jwt_identity()
        if space.owner_id != current_user_id:
            return {'message': 'Unauthorized'}, 403
        image_data = image_file.read()
        upload_result = upload_image(image_data)
        if not upload_result:
            return {'message': 'Failed to upload image'}, 500
        image_url = upload_result['url']
        public_id = upload_result['public_id']
        image = space.add_image(image_url=image_url, public_id=public_id, is_primary=is_primary)
        db.session.commit()
        return {'message': 'Image added successfully', 'image_id': image.id}, 201

@spaces_ns.route('/<int:space_id>/images/<int:image_id>')
class SpaceImageDetail(Resource):
    @jwt_required()
    def delete(self, space_id, image_id):
        """Remove an image from a space"""
        space = Space.query.get_or_404(space_id)
        current_user_id = get_jwt_identity()
        if space.owner_id != current_user_id:
            return {'message': 'Unauthorized'}, 403
        success = space.remove_image(image_id)
        if success:
            db.session.commit()
            return {'message': 'Image removed successfully'}
        else:
            return {'message': 'Image not found'}, 404

@spaces_ns.route('/<int:space_id>/images/<int:image_id>/primary')
class SpaceImagePrimary(Resource):
    @jwt_required()
    def patch(self, space_id, image_id):
        """Set an image as the primary image for a space"""
        space = Space.query.get_or_404(space_id)
        current_user_id = get_jwt_identity()
        if space.owner_id != current_user_id:
            return {'message': 'Unauthorized'}, 403
        success = space.set_primary_image(image_id)
        if success:
            db.session.commit()
            return {'message': 'Primary image set successfully'}
        else:
            return {'message': 'Image not found'}, 404
