from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash
from ..models.user import User, UserRole
from ..utils.auth import generate_verification_token, verify_token
from ..utils.email import send_verification_email
from ..models.base import db
import json

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'first_name', 'last_name', 'role']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'User already exists'}), 400
    
    # Validate role
    try:
        role = UserRole(data['role'])
    except ValueError:
        return jsonify({'message': 'Invalid role'}), 400
    
    # Create new user
    user = User(
        email=data['email'],
        password=data['password'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        role=role
    )
    
    # Generate verification token
    verification_token = generate_verification_token()
    user.verification_token = verification_token
    
    # Save user
    user.save()
    
    # Send verification email
    send_verification_email(user, verification_token)
    
    return jsonify({'message': 'User registered successfully. Please check your email for verification.'}), 201

@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    """Verify user's email address"""
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({'message': 'Token is required'}), 400
    
    user = User.query.filter_by(verification_token=token).first()
    if not user:
        return jsonify({'message': 'Invalid or expired token'}), 400
    
    user.is_verified = True
    user.verification_token = None
    user.save()
    
    return jsonify({'message': 'Email verified successfully'}), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT tokens"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid email or password'}), 401
    
    if not user.is_verified:
        return jsonify({'message': 'Please verify your email first'}), 403
    
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    return jsonify({'access_token': access_token}), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user's information"""
    current_user_id = get_jwt_identity()
    user = User.get_by_id(current_user_id)
    return jsonify(user.to_dict()), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user"""
    # In a stateless JWT system, we don't need to do anything on the server side
    # The client should remove the tokens from local storage
    return jsonify({'message': 'Successfully logged out'}), 200

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Request password reset"""
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'message': 'Email is required'}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    reset_token = generate_verification_token()
    user.verification_token = reset_token
    user.save()
    
    # Send password reset email
    send_verification_email(user, reset_token)
    
    return jsonify({'message': 'Password reset instructions sent to your email'}), 200

@auth_bp.route('/update-password', methods=['POST'])
def update_password():
    """Update password using reset token"""
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')
    
    if not token or not new_password:
        return jsonify({'message': 'Token and new password are required'}), 400
    
    user = User.query.filter_by(verification_token=token).first()
    if not user:
        return jsonify({'message': 'Invalid or expired token'}), 400
    
    user.set_password(new_password)
    user.verification_token = None
    user.save()
    
    return jsonify({'message': 'Password updated successfully'}), 200 