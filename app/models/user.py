from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import enum

class UserRole(str, enum.Enum):
    EMPLOYEE = "EMPLOYEE"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"

from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.EMPLOYEE)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)
    join_date = db.Column(db.Date, nullable=True)
    resident_reg_number = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    position = db.Column(db.String(100), nullable=True) # Used for 'Rank/직급'
    card_number = db.Column(db.String(20), nullable=True) # Corporate Card Number
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    team = db.relationship('Team', foreign_keys=[team_id], backref='members')
    signature = db.relationship('UserSignature', uselist=False, backref='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Team(db.Model):
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Manager relationship (careful with circular imports if separating files, here ok)
    manager = db.relationship('User', remote_side=[User.id], foreign_keys=[manager_id], backref=db.backref('managed_team', uselist=False))

class SignatureType(str, enum.Enum):
    DRAWN = "DRAWN"
    AUTO_TEXT = "AUTO_TEXT" 
    STAMP_IMAGE = "STAMP_IMAGE"

class UserSignature(db.Model):
    __tablename__ = 'user_signatures'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    signature_type = db.Column(db.Enum(SignatureType), default=SignatureType.AUTO_TEXT)
    image_path = db.Column(db.String(500), nullable=True) # if STAMP or DRAWN
    text_content = db.Column(db.String(100), nullable=True) # if AUTO_TEXT
