from flask import Blueprint, request, jsonify
from backend.models import User  # assuming your SQLAlchemy models are in models.py
from routes.auth_utils import token_required
from backend import db
users_bp = Blueprint('users', __name__, url_prefix='/users')


@users_bp.route('/', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = [{
        "sl_no": user.sl_no,
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email
    } for user in users]
    return jsonify(user_list)


@users_bp.route('/', methods=['POST'])
def add_user():
    data = request.json
    new_user = User(
        name=data['name'],
        email=data['email'],
        user_id=data.get('user_id', f"user_{data['email']}"),  # fallback
        password_hash=data['password_hash']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"user_id": new_user.user_id}), 201


@users_bp.route('/me', methods=['GET'])
@token_required
def get_me():
    user = User.query.filter_by(user_id=request.user_id).first()
    if user:
        return jsonify({
            "user_id": user.user_id,
            "name": user.name,
            "email": user.email
        })
    return jsonify({"error": "User not found"}), 404
