from flask import Blueprint, request, jsonify
from backend import db
from backend.models import Category, User

categories_bp = Blueprint('categories', __name__, url_prefix='/categories')


@categories_bp.route('/', methods=['GET'])
def get_categories():
    categories = db.session.query(Category).all()
    
    result = []
    for cat in categories:
        result.append({
            "category_id": cat.category_id,
            "user_id": cat.user_id,
            "name": cat.name,
            "type": cat.type
        })

    return jsonify(result)


@categories_bp.route('/', methods=['POST'])
def add_category():
    data = request.json
    user_id = data.get('user_id')
    name = data.get('name')
    category_type = data.get('type')

    # Validate user
    user = db.session.query(User).filter_by(user_id=user_id).first()
    if not user:
        return jsonify({"error": "User ID does not exist"}), 400

    # Insert new category
    category = Category(
        user_id=user_id,
        name=name,
        type=category_type
    )
    db.session.add(category)
    db.session.commit()

    return jsonify({"category_id": category.category_id}), 201
