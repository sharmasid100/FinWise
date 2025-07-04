from datetime import datetime
from backend import db
from flask_login import UserMixin
class User(db.Model , UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.String, primary_key = True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    categories = db.relationship('Category', back_populates='user', cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', back_populates='user', cascade='all, delete-orphan')

    def get_id(self):
        return str(self.user_id)

class Category(db.Model):
    __tablename__ = 'categories'

    category_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.user_id', ondelete='CASCADE'))
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'

    # Relationships
    user = db.relationship('User', back_populates='categories')
    transactions = db.relationship('Transaction', back_populates='category')

    # Check constraint
    __table_args__ = (
        db.CheckConstraint("type IN ('income', 'expense')", name='check_category_type'),
    )

class Transaction(db.Model):
    __tablename__ = 'transactions'

    transaction_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.user_id', ondelete='CASCADE'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id', ondelete='SET NULL'))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'

    # Relationships
    user = db.relationship('User', back_populates='transactions')
    category = db.relationship('Category', back_populates='transactions')

    # Check constraint
    __table_args__ = (
        db.CheckConstraint("type IN ('income', 'expense')", name='check_transaction_type'),
    )