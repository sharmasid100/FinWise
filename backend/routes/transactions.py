from flask import Blueprint, request, jsonify
from backend import db
from backend.models import Transaction, Category, User 

transactions_bp = Blueprint('transactions', __name__, url_prefix='/transactions')


@transactions_bp.route('/', methods=['GET'])
def get_transactions():
    transactions = db.session.query(
        Transaction.transaction_id,
        Transaction.amount,
        Transaction.transaction_date,
        Transaction.description,
        Transaction.type,
        Category.name.label('category'),
        User.name.label('user')
    ).join(Category, Transaction.category_id == Category.category_id) \
     .join(User, Transaction.user_id == User.user_id) \
     .all()

    result = []
    for txn in transactions:
        result.append({
            "transaction_id": txn.transaction_id,
            "amount": float(txn.amount),
            "transaction_date": txn.transaction_date.strftime('%Y-%m-%d'),
            "description": txn.description,
            "type": txn.type,
            "category": txn.category,
            "user": txn.user
        })

    return jsonify(result)


@transactions_bp.route('/', methods=['POST'])
def add_transaction():
    data = request.json
    user_id = data.get('user_id')
    category_id = data.get('category_id')
    amount = data.get('amount')
    date = data.get('transaction_date')
    description = data.get('description')
    txn_type = data.get('type')

    # Validate user
    user = db.session.query(User).filter_by(user_id=user_id).first()
    if not user:
        return jsonify({"error": "User ID does not exist"}), 400

    # Validate category
    category = db.session.query(Category).filter_by(category_id=category_id).first()
    if not category:
        return jsonify({"error": "Category ID does not exist"}), 400

    # Insert transaction
    txn = Transaction(
        user_id=user_id,
        category_id=category_id,
        amount=amount,
        transaction_date=date,
        description=description,
        type=txn_type
    )
    db.session.add(txn)
    db.session.commit()

    return jsonify({"transaction_id": txn.transaction_id}), 201
