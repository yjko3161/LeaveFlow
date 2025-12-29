from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    
    # Config
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///flexlite.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Use absolute path for uploads
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    app.config['UPLOAD_DIR'] = os.path.join(base_dir, os.getenv('UPLOAD_DIR', 'uploads'))

    # Init Extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # User Loader
    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import Models for detection
    with app.app_context():
        from app.models import user, approval, leave, expense, certificate, quote, company
        # db.create_all() # We will do this via seed script

    # Context Processor for Notifications
    @app.context_processor
    def inject_notifications():
        if not current_user.is_authenticated:
            return dict(unread_count=0)
            
        from app.models.approval import ApprovalRequest, RequestStatus
        
        pending_statuses = [RequestStatus.SUBMITTED, RequestStatus.IN_PROGRESS]
        
        if current_user.role == 'ADMIN':
             count = ApprovalRequest.query.filter(ApprovalRequest.status.in_(pending_statuses)).count()
        elif current_user.role == 'MANAGER':
            from app.models.user import User
            count = ApprovalRequest.query.join(User, ApprovalRequest.requester_id == User.id)\
                .filter(ApprovalRequest.status.in_(pending_statuses), User.team_id == current_user.team_id).count()
        else:
            count = 0
            
        return dict(unread_count=count)

    # Register Filters
    from app.utils.formatters import num_to_kor
    app.jinja_env.filters['num_to_kor'] = num_to_kor

    # Register Blueprints
    from app.routes import auth, main, leave, approval, expense, certificate, export, quote, settings
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(main.bp)
    app.register_blueprint(leave.bp)
    app.register_blueprint(approval.bp)
    app.register_blueprint(expense.bp)
    app.register_blueprint(certificate.bp)
    app.register_blueprint(export.bp)
    app.register_blueprint(quote.bp)
    app.register_blueprint(settings.bp)

    return app
