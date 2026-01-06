from app import db
from datetime import datetime
import enum

class StampGroup(str, enum.Enum):
    GENERAL = "general"
    CORP = "corp"
    SIGN = "sign"

class StampAssetType(str, enum.Enum):
    STAMP = "stamp"
    SIGN = "sign"

class StampTemplate(db.Model):
    __tablename__ = 'stamp_templates'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    group = db.Column(db.Enum(StampGroup), nullable=False)
    spec_json = db.Column(db.JSON, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

class StampAsset(db.Model):
    __tablename__ = 'stamp_assets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.Enum(StampAssetType), nullable=False)
    template_code = db.Column(db.String(50), nullable=True) # None if uploaded
    text = db.Column(db.String(100), nullable=True)
    options_json = db.Column(db.JSON, nullable=True)
    file_svg_path = db.Column(db.String(500), nullable=False)
    file_png_path = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('stamp_assets', lazy=True))
