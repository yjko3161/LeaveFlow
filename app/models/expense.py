from app import db
from datetime import datetime

class ExpenseCategory(db.Model):
    __tablename__ = 'expense_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), nullable=True) # Account code

class ExpenseReceipt(db.Model):
    __tablename__ = 'expense_receipts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('expense_categories.id'), nullable=False)
    
    usage_date = db.Column(db.Date, nullable=False)
    merchant = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=True) # Receipt image
    
    report_id = db.Column(db.Integer, db.ForeignKey('expense_reports.id'), nullable=True) # Linked when submitted
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    category = db.relationship('ExpenseCategory')
    file = db.relationship('File', foreign_keys=[file_id])

class ExpenseReport(db.Model):
    __tablename__ = 'expense_reports'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    total_amount = db.Column(db.Integer, default=0)
    
    status_local = db.Column(db.String(20), default="DRAFT")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('ExpenseReceipt', backref='report')
    user = db.relationship('User')
