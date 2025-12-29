from app import db
from datetime import datetime
import enum

class CertificateType(str, enum.Enum):
    EMPLOYMENT = "EMPLOYMENT" # 재직증명서
    CAREER = "CAREER" # 경력증명서
    INCOME = "INCOME" # 소득증명서

class CertificateRequest(db.Model):
    __tablename__ = 'certificate_requests'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    cert_type = db.Column(db.Enum(CertificateType), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    issue_to = db.Column(db.String(100), nullable=True) # 제출처
    
    status_local = db.Column(db.String(20), default="DRAFT")
    
    issued_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='certificates')
