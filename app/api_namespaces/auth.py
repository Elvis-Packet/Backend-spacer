from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import create_access_token
from app.models import User
from app.models.user import UserRole
from sqlalchemy.exc import IntegrityError

auth_ns = Namespace('auth', description='Authentication operations')

user_registration_model = auth_ns.model('UserRegistration', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
    'first_name': fields.String(required=True, description='First name'),
    'last_name': fields.String(required=True, description='Last name'),
    'role': fields.String(required=False, description='User role (CLIENT or SPACE_OWNER)')
})

user_login_model = auth_ns.model('UserLogin', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(user_registration_model)
    @auth_ns.response(201, 'User created successfully')
    def post(self):
        """Register a new user"""
        data = request.get_json()
        try:
            role_str = data.get('role', 'CLIENT').upper()
            if role_str not in ['CLIENT', 'SPACE_OWNER']:
                return {'message': 'Invalid role'}, 400
            role = UserRole[role_str]
            user = User(
                data['email'],
                data['password'],
                data['first_name'],
                data['last_name'],
                role
            )
            user.save()
            return {'message': 'User created successfully'}, 201
        except IntegrityError as e:
            if 'users_email_key' in str(e.orig):
                return {'message': 'Email already registered'}, 400
            else:
                return {'message': 'Registration failed'}, 500

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(user_login_model)
    @auth_ns.response(200, 'Login successful')
    @auth_ns.response(401, 'Invalid credentials')
    def post(self):
        """Login user and return JWT token"""
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        if user and user.check_password(data['password']):
            additional_claims = {'role': user.role.value}
            access_token = create_access_token(identity=user.id, additional_claims=additional_claims)
            return {'access_token': access_token}, 200
        return {'message': 'Invalid credentials'}, 401
