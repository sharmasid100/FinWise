from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from backend.models import User
from backend import db
import jwt, datetime, os
from dotenv import load_dotenv

load_dotenv()

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

JWT_SECRET = os.getenv("JWT_SECRET", "your_default_secret")
JWT_EXPIRY_MINUTES = 60

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    # Check if email already exists
    existing_user = db.session.query(User).filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already exists"}), 400

    # Create and insert new user
    hashed_pw = generate_password_hash(password)
    new_user = User(name=name, email=email, password_hash=hashed_pw, user_id=f"user_{datetime.datetime.now().timestamp()}")
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered"}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = db.session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode({
        'user_id': user.user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=JWT_EXPIRY_MINUTES)
    }, JWT_SECRET, algorithm='HS256')

    return jsonify({"token": token})
