#Interpreter (scripts-qCppuchw)
from datetime import datetime, timedelta

from flask import request, render_template, redirect, url_for, jsonify , session , flash , session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user, login_required, current_user
from decimal import Decimal
from sqlalchemy.exc import SQLAlchemyError

from backend import create_app
app = create_app()

from backend import db
from backend.models import User , Transaction , Category
from backend.routes.users import users_bp
from backend.routes.categories import categories_bp
from backend.routes.transactions import transactions_bp
from backend.routes.auth import auth_bp

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, str(user_id))


@app.route('/')
def home():
    # Check if user is on mobile device
    user_agent = request.headers.get('User-Agent', '').lower()
    mobile_agents = ['iphone', 'android', 'blackberry', 'mobile']
    
    if any(agent in user_agent for agent in mobile_agents):
        return render_template('home_res.html')
    else:
        return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        user_id = request.form.get('user_id', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not all([name, user_id, email, password, confirm_password]):
            return render_template('register.html', error='Please fill in all fields', name=name, user_id=user_id, email=email)

        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match', name=name, user_id=user_id, email=email)

        if len(password) < 6 or not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
            return render_template('register.html', error='Password must be at least 6 characters with letters and numbers', name=name, user_id=user_id, email=email)

        existing = db.session.execute(
            db.select(User).where((User.user_id == user_id) | (User.email == email))
        ).scalar()

        if existing:
            return render_template('register.html', error='User ID or email already exists', name=name, user_id=user_id, email=email)

        new_user = User(
            name=name,
            user_id=user_id,
            email=email,
            password_hash=generate_password_hash(password)
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login', registered=True))

    return render_template('register.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')

        if not user_id or not password:
            return render_template('login.html', error='Please fill in all fields')

        user = db.session.execute(
            db.select(User).where(User.user_id == user_id)
        ).scalar()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))

        return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')



def get_sum(user_id, transaction_type, start_date=None, end_date=None):
    """Helper function to get sum of transactions with optional date range"""
    query = Transaction.query.filter_by(
        user_id=user_id,
        type=transaction_type
    )
    
    # Only filter by date if the Transaction model has date attribute
    if hasattr(Transaction, 'date') and start_date and end_date:
        query = query.filter(Transaction.date.between(start_date, end_date))
    
    return float(sum(t.amount for t in query.all()))


def get_chart_data(user_id, start_date, end_date, time_period):
    """Get chart data based on time period"""
    # Get all transactions in date range
    transactions = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.date.between(start_date, end_date)
    ).all()
    
    # Initialize chart data structure
    chart_data = {
        "income": [],
        "expenses": [],
        "labels": [],
        "categories": [],
        "category_totals": []
    }
    
    # Group by time period
    if time_period == 'week':
        # Group by day
        days = [(end_date - timedelta(days=i)).strftime('%A') for i in range(6, -1, -1)]
        chart_data['labels'] = days
        
        # Initialize daily totals
        daily_income = [0.0] * 7
        daily_expenses = [0.0] * 7
        
        for t in transactions:
            days_diff = (end_date - t.date).days
            if 0 <= days_diff <= 6:  # Last 7 days
                idx = 6 - days_diff
                if t.type == 'income':
                    daily_income[idx] +=float(t.amount)
                else:
                    daily_expenses[idx] +=float(t.amount)
        
        chart_data['income'] = daily_income
        chart_data['expenses'] = daily_expenses
        
    elif time_period == 'quarter':
        # Group by month
        months = []
        current = start_date
        while current <= end_date:
            months.append(current.strftime('%B'))
            # Move to next month
            if current.month == 12:
                current = current.replace(year=current.year+1, month=1)
            else:
                current = current.replace(month=current.month+1)
        
        chart_data['labels'] = months[:3]  # Only show 3 months for quarter
        
        # Initialize monthly totals
        monthly_income = [0.0] * 3
        monthly_expenses = [0.0] * 3
        
        for t in transactions:
            month_idx = (t.date.year - start_date.year) * 12 + (t.date.month - start_date.month)
            if 0 <= month_idx <= 2:  # Only 3 months in quarter
                if t.type == 'income':
                    monthly_income[month_idx] +=float(t.amount)
                else:
                    monthly_expenses[month_idx] +=float(t.amount)
        
        chart_data['income'] = monthly_income
        chart_data['expenses'] = monthly_expenses
        
    else:  # month
        # Group by week
        weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
        chart_data['labels'] = weeks
        
        # Initialize weekly totals
        weekly_income = [Decimal(0) for _ in range(4)]
        weekly_expenses = [Decimal(0) for _ in range(4)]
        
        for t in transactions:
            week_num = (t.date.day - 1) // 7
            if 0 <= week_num <= 3:  # Only 4 weeks in month
                if t.type == 'income':
                    weekly_income[week_num] += t.amount
                else:
                    weekly_expenses[week_num] +=t.amount
        
        chart_data['income'] = weekly_income
        chart_data['expenses'] = weekly_expenses
    
    # Get expense categories breakdown (for pie chart)
    expense_categories = {}
    for t in transactions:
        if t.type == 'expense':
            category_name = t.category.name if t.category else "Uncategorized"

            if category_name not in expense_categories:
                expense_categories[category_name] = 0.0
            expense_categories[category_name] += float(t.amount)
    
    chart_data['categories'] = list(expense_categories.keys())
    chart_data['category_totals'] = list(expense_categories.values())
    
    return chart_data

def get_recent_transactions(user_id, start_date=None, end_date=None, limit=5):
    """Get recent transactions with optional date range"""
    query = Transaction.query.filter_by(user_id=user_id)
    
    # Only filter by date if the Transaction model has date attribute
    if hasattr(Transaction, 'date'):
        if start_date and end_date:
            query = query.filter(Transaction.date.between(start_date, end_date))
        query = query.order_by(Transaction.date.desc())
    else:
        query = query.order_by(Transaction.id.desc())  # Fallback to ID if no date
    
    transactions = query.limit(limit).all()
    
    return [{
        "description": t.description,
        "category": t.category.name if t.category else "Uncategorized",
        "amount": float(t.amount),
        "type": t.type,
        "date": t.date.strftime('%Y-%m-%d') if hasattr(t, 'date') else "N/A"
    } for t in transactions]

def get_all_transactions(user_id, start_date=None, end_date=None):
    """Get all transactions with optional date range filtering"""
    query = Transaction.query.filter_by(user_id=user_id)
    
    # Filter by date range if specified and model has date attribute
    if hasattr(Transaction, 'date'):
        if start_date and end_date:
            query = query.filter(Transaction.date.between(start_date, end_date))
        query = query.order_by(Transaction.date.desc())
    else:
        query = query.order_by(Transaction.id.desc())  # Fallback sorting
    
    transactions = query.all()  # Remove limit to get all
    
    return [{
        "description": t.description,
        "category": t.category.name if t.category else "Uncategorized",
        "amount": float(t.amount),
        "type": t.type,
        "date": t.date.strftime('%Y-%m-%d') if hasattr(t, 'date') else "N/A",
        "transaction_id": t.transaction_id  # Added ID for reference
    } for t in transactions]


@app.route('/api/categories', methods=['GET'])
@login_required
def get_categories():
    try:
        categories = Category.query.filter_by(user_id=current_user.user_id).all()
        return jsonify({
            'income': [c.name for c in categories if c.type == 'income'],
            'expense': [c.name for c in categories if c.type == 'expense']
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = current_user.user_id
    
    # Calculate default date range (last 30 days)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Get default summary data
    summary = {
        "income": get_sum(user_id, 'income', start_date, end_date),
        "expenses": get_sum(user_id, 'expense', start_date, end_date),
        "net": get_sum(user_id, 'income', start_date, end_date) - get_sum(user_id, 'expense', start_date, end_date)
    }

    # Get default chart data
    chart_data = get_chart_data(user_id, start_date, end_date, 'month')
    
    # Get default transactions
    transactions = get_recent_transactions(user_id, start_date, end_date)

    return render_template('dashboard.html',
        summary=summary,
        charts=chart_data,
        transactions=transactions
    )

@app.route('/api/dashboard/data')
@login_required
def dashboard_data():
    user_id = current_user.user_id
    time_period = request.args.get('time_period', 'month')
    
    # Calculate date range based on time period
    end_date = datetime.now().date()
    
    if time_period == 'week':
        start_date = end_date - timedelta(days=7)
    elif time_period == 'quarter':
        start_date = end_date - timedelta(days=90)
    else:  # month (default)
        start_date = end_date - timedelta(days=30)
    
    # Get summary data
    income = get_sum(user_id, 'income', start_date, end_date)
    expenses = get_sum(user_id, 'expense', start_date, end_date)
    
    summary = {
        "income": income,
        "expenses": expenses,
        "net": income - expenses
    }

    # Get chart data
    chart_data = get_chart_data(user_id, start_date, end_date, time_period)

    # Get recent transactions
    transactions = get_recent_transactions(user_id, start_date, end_date)

    return jsonify({
        "success": True,
        "summary": summary,
        "charts": chart_data,
        "transactions": transactions
    })


@app.route('/record_transactions')
@login_required
def record():
    return render_template('record.html')


@app.route('/transactions')
@login_required
def transactions():
    # Get transactions for the current user (last 30 days by default)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    transactions = get_all_transactions(
        user_id=current_user.user_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return render_template('transactions.html', transactions=transactions)


@app.route('/goals')
@login_required
def goals():
    return render_template('goals.html')

@app.route('/learnmore')
def learnmore():
    return render_template('learn_more.html')
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        # Handle name update
        new_name = request.form.get('name')
        if new_name and new_name != current_user.name:
            current_user.name = new_name
            db.session.commit()
            flash('Name updated successfully', 'success')
        
        # Handle theme preference
        theme_preference = request.form.get('theme')
        if theme_preference in ['light', 'dark']:
            # Store in database or session
            session['theme'] = theme_preference
            flash('Theme preference updated', 'success')
        
        return redirect(url_for('settings'))
    
    return render_template('settings.html', 
                         user_id=current_user.user_id,
                         name=current_user.name,
                         email=current_user.email,
                         created_at=current_user.created_at)


@app.route('/api/transactions', methods=['POST'])
@login_required
def add_transaction():


    if not request.is_json:
        return jsonify({'message': 'Request must be JSON'}), 400

    data = request.get_json()
    
    # Validate required fields
    required_fields = ['amount', 'type', 'category', 'date']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'message': f'Missing required field: {field}'}), 400

    try:
        # Validate amount
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({'message': 'Amount must be positive'}), 400

        # Validate transaction type
        if data['type'] not in ['income', 'expense']:
            return jsonify({'message': 'Invalid transaction type'}), 400

        # Parse date
        try:
            transaction_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400

        # Find or validate category
        category = Category.query.filter_by(
            user_id=current_user.user_id,
            name=data['category'],
            type=data['type']
        ).first()

        if not category:
            return jsonify({'message': 'Invalid category for this transaction type'}), 400

        # Create new transaction
        new_transaction = Transaction(
            user_id=current_user.user_id,
            category_id=category.category_id,
            amount=amount,
            date=transaction_date,
            description=data.get('description', ''),
            type=data['type']
        )

        db.session.add(new_transaction)
        db.session.commit()

        return jsonify({
            'message': 'Transaction recorded successfully',
            'transaction': {
                'id': new_transaction.transaction_id,
                'amount': float(new_transaction.amount),
                'type': new_transaction.type,
                'category': category.name,
                'date': new_transaction.date.isoformat(),
                'description': new_transaction.description
            }
        }), 201

    except ValueError as e:
        return jsonify({'message': f'Invalid data format: {str(e)}'}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'message': f'Server error: {str(e)}'}), 500


from flask import session, jsonify

@app.route('/toggle_theme', methods=['POST'])
def toggle_theme():
    data = request.get_json()
    theme = data.get('theme', 'dark')
    session['theme'] = theme
    return jsonify({'success': True})

@app.route('/update_name', methods=['POST'])
def update_name():
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    data = request.get_json()
    new_name = data.get('name', '').strip()
    
    if not new_name:
        return jsonify({'success': False, 'error': 'Name cannot be empty'})
    
    try:
        current_user.name = new_name
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
@app.route('/logout', methods=['GET' , 'POST'])
def logout():
    session.clear()
    return redirect(url_for('home'))



# Register Blueprints
app.register_blueprint(users_bp)
app.register_blueprint(categories_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(auth_bp)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
