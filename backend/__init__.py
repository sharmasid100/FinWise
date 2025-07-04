import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

# Initialize extensions without app context
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()

def create_app():
    # Load environment variables
    load_dotenv()
    
    # Create Flask app instance
    app = Flask(
        __name__,
        template_folder='../frontend/templates',
        static_folder='../frontend/static'
    )
    
    # App configuration
    app.config.update(
        SECRET_KEY=os.urandom(24),
        SQLALCHEMY_DATABASE_URI=os.getenv("DB_URL"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        WTF_CSRF_ENABLED=False,
        WTF_CSRF_SECRET_KEY= os.urandom(24)
    )
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    
    # Import models within app context
    with app.app_context():
        db.create_all() 
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return "404 Not Found", 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return "500 Internal Server Error", 500
    
    return app