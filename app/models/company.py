from app import db

class CompanyInfo(db.Model):
    __tablename__ = 'company_info'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    owner_name = db.Column(db.String(50))
    registration_number = db.Column(db.String(20))
    address = db.Column(db.String(200))
    business_type = db.Column(db.String(50)) # 업태
    business_item = db.Column(db.String(50)) # 종목
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    stamp_path = db.Column(db.String(200)) # 대표직인 이미지 경로
