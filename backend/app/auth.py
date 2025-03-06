from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
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

@bp.route('/change_password', methods=['POST'])
@login_required  # Ensure that the user is logged in
def change_password():
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    # Validate current password and new password
    if not current_password or not new_password:
        return jsonify({"error": "Current password and new password are required"}), 400

    # Check if the current password matches the user's password
    if not current_user.check_password(current_password):
        return jsonify({"error": "Current password is incorrect"}), 400

    # Set the new password
    current_user.set_password(new_password)

    # Commit the changes to the database
    db.session.commit()

    return jsonify({"message": "Password updated successfully"}), 200

# New route to check if the user is logged in
@bp.route('/check_session', methods=['GET'])
@login_required  # Ensure the user is logged in
def check_session():
    return jsonify({
        "message": "Session is active",
        "user": {
            "email": current_user.email,
            "created_at": current_user.created_at
        }
    }), 200
