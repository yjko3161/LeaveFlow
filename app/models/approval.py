from app import db
from datetime import datetime
import enum

class RequestStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    IN_PROGRESS = "IN_PROGRESS"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

class ApprovalRequest(db.Model):
    __tablename__ = 'approval_requests'

    id = db.Column(db.Integer, primary_key=True)
    doc_type = db.Column(db.String(50), nullable=False) # LEAVE, EXPENSE, CERTIFICATE
    doc_id = db.Column(db.Integer, nullable=False) # Linked Document ID
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum(RequestStatus), default=RequestStatus.DRAFT)
    current_step_order = db.Column(db.Integer, default=1)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    steps = db.relationship('ApprovalStep', backref='request', order_by='ApprovalStep.step_order')
    actions = db.relationship('ApprovalAction', backref='request', order_by='ApprovalAction.created_at')
    
    requester = db.relationship('User', foreign_keys=[requester_id])

class ApprovalStep(db.Model):
    __tablename__ = 'approval_steps'

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('approval_requests.id'), nullable=False)
    step_order = db.Column(db.Integer, nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Specific user
    # approver_role? For now specific user derived from template
    
    status = db.Column(db.String(20), default="PENDING") # PENDING, APPROVED, REJECTED, SKIPPED
    
    approver = db.relationship('User')

class ApprovalAction(db.Model):
    __tablename__ = 'approval_actions'

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('approval_requests.id'), nullable=False)
    step_id = db.Column(db.Integer, db.ForeignKey('approval_steps.id'), nullable=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(20), nullable=False) # APPROVE, REJECT, SUBMIT, COMMENTS
    comment = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    actor = db.relationship('User')
