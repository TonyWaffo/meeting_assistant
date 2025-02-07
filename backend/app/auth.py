from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from app.models import User
from app import db

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Validate email and password
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists"}), 400

    # Create new user
    user = User(email=email)
    user.set_password(password)
    
    # Add user to database
    db.session.add(user)
    db.session.commit()

    # Return success response with created_at
    return jsonify({
        "message": "User registered successfully",
        "user": {
            "email": user.email,
            "created_at": user.created_at
        }
    }), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    # Check if user exists and password is correct
    if user and user.check_password(password):
        login_user(user)

        return jsonify({
            "message": "Logged in successfully",
            "user": {
                "email": user.email,
                "created_at": user.created_at
            }
        }), 200
    
    return jsonify({"error": "Invalid credentials"}), 401

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200
