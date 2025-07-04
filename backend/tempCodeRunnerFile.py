from datetime import datetime, timedelta

from flask import request, render_template, redirect, url_for, jsonify , session , flash
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