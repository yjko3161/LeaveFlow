from app import db
from datetime import datetime
import enum

class LeaveType(str, enum.Enum):
    ANNUAL = "ANNUAL" # 연차
    SICK = "SICK" # 병가
    HALF = "HALF" # 반차

class LeaveBalance(db.Model):
    __tablename__ = 'leave_balances'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    granted = db.Column(db.Float, default=0.0)
    used = db.Column(db.Float, default=0.0)
    remaining = db.Column(db.Float, default=0.0)

class LeaveRequest(db.Model):
    __tablename__ = 'leave_requests'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    leave_type = db.Column(db.Enum(LeaveType), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    days = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(255), nullable=True)
    
    # Cache status for UI, but ApprovalRequest is source of truth
    status_local = db.Column(db.String(20), default="DRAFT") 
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='leave_requests')
