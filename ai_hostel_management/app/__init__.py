from flask import Flask, render_template
from flask_login import LoginManager
from config.config import config
import os
from app.models import db, User
from app.routes.auth import auth_bp
from app.routes.admin import admin_bp
from app.routes.student import student_bp
from app.routes.api import api_bp
from app.routes.chatbot import chatbot_bp

import os

def create_app(config_name='development'):
    """Application factory"""
    
    # Initialize Flask app with root-level templates/static
    # Flask normally looks for templates relative to the module (__file__)
    # which would be app/templates. Our templates live at the workspace root,
    # so we override the folders accordingly.
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    app = Flask(__name__,
                template_folder=os.path.join(base_dir, 'templates'),
                static_folder=os.path.join(base_dir, 'static'))
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create upload folder
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(chatbot_bp)
    
    # Context processors
    @app.context_processor
    def inject_user():
        from flask import session
        user = None
        if 'username' in session:
            user = User.query.filter_by(username=session['username']).first()
        return dict(current_user=user)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403
    
    return app

# Create app instance
app = create_app(os.getenv('FLASK_ENV', 'development'))