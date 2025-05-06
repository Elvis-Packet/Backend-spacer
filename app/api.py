from flask import Blueprint
from app.api_namespaces.auth import auth_ns
from app.api_namespaces.spaces import spaces_ns
from app.api_namespaces.bookings import bookings_ns
from app.api_namespaces.testimonials import testimonials_ns
from app.api_namespaces.admin import admin_ns
from flask_restx import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import UserRole, User  # Import UserRole and User from the appropriate module

api_bp = Blueprint('api', __name__)

authorizations = {
    'bearerAuth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Enter 'Bearer <JWT>' to authorize"
    }
}

api = Api(api_bp,
          version='1.0',
          title='Spacer API',
          description='API for managing spaces, bookings, and user accounts',
          doc='/docs/',
          authorizations=authorizations,
          security='bearerAuth')

from app.api_namespaces.admin import user_model

api.add_namespace(auth_ns)
api.add_namespace(spaces_ns)
api.add_namespace(bookings_ns)
api.add_namespace(testimonials_ns)
api.add_namespace(admin_ns)

# Admin Routes
@admin_ns.route('/users')
class UserList(Resource):
    @jwt_required()
    @admin_ns.marshal_list_with(user_model)
    def get(self):
        """Get all users (admin only)"""
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if current_user.role != UserRole.ADMIN:
            return {'message': 'Unauthorized'}, 403
        return User.query.all()

@admin_ns.route('/users/<int:user_id>')
class UserDetail(Resource):
    @jwt_required()
    @admin_ns.marshal_with(user_model)
    def get(self, user_id):
        """Get user details (admin only)"""
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if current_user.role != UserRole.ADMIN:
            return {'message': 'Unauthorized'}, 403
        return User.query.get_or_404(user_id)

    @jwt_required()
    def delete(self, user_id):
        """Delete a user (admin only)"""
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if current_user.role != UserRole.ADMIN:
            return {'message': 'Unauthorized'}, 403
        user = User.query.get_or_404(user_id)
        user.delete()
        return {'message': 'User deleted successfully'} 