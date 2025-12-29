from app import db
from datetime import datetime

class Quote(db.Model):
    __tablename__ = 'quotes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(200), nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    total_amount = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Status (Local)
    status_local = db.Column(db.String(20), default='DRAFT') # DRAFT, SUBMITTED, APPROVED
    
    # Provider Info Snapshot
    provider_company_name = db.Column(db.String(100))
    provider_owner_name = db.Column(db.String(50))
    provider_reg_number = db.Column(db.String(20))
    provider_address = db.Column(db.String(200))
    provider_business_type = db.Column(db.String(50))
    provider_business_item = db.Column(db.String(50))
    provider_phone = db.Column(db.String(20))
    provider_stamp_path = db.Column(db.String(200))
    
    items = db.relationship('QuoteItem', backref='quote', cascade='all, delete-orphan')

class QuoteItem(db.Model):
    __tablename__ = 'quote_items'
    
    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'))
    description = db.Column(db.String(200), nullable=False)
    spec = db.Column(db.String(50)) # 규격
    unit = db.Column(db.String(20)) # 단위
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Integer, default=0)
    amount = db.Column(db.Integer, default=0) # qty * unit_price

