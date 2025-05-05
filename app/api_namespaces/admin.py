from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User
from app.models.user import UserRole

admin_ns = Namespace('admin', description='Admin operations')

user_model = admin_ns.model('User', {
    'id': fields.Integer(readonly=True),
    'email': fields.String(required=True),
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'role': fields.String(required=True),
    'is_verified': fields.Boolean(default=False),
    'profile_picture': fields.String,
    'phone_number': fields.String
})

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
