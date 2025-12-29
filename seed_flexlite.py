from app.models.company import CompanyInfo
from app import create_app, db
from app.models.user import User, UserRole, Team
from app.models.leave import LeaveBalance
from datetime import date
from dotenv import load_dotenv

load_dotenv()

app = create_app()

def seed():
    with app.app_context():
        print(f"SEEDING DATABASE: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        
        # Teams
        hr_team = Team(name="HR Team")
        dev_team = Team(name="Development Team")
        db.session.add(hr_team)
        db.session.add(dev_team)
        db.session.commit()
        
        # Users
        admin = User(
            email="admin@flexlite.com",
            name="Admin User",
            role=UserRole.ADMIN,
            team_id=hr_team.id,
            join_date=date(2020, 1, 1)
        )
        admin.set_password("password")
        
        manager = User(
            email="manager@flexlite.com",
            name="Manager Bob",
            role=UserRole.MANAGER,
            team_id=dev_team.id,
            join_date=date(2021, 5, 1)
        )
        manager.set_password("password")
        
        employee = User(
            email="employee@flexlite.com",
            name="Employee Alice",
            role=UserRole.EMPLOYEE,
            team_id=dev_team.id,
            join_date=date(2023, 1, 1)
        )
        employee.set_password("password")
        
        db.session.add_all([admin, manager, employee])
        db.session.commit()
        
        # Team Manager Assignment
        dev_team.manager_id = manager.id
        db.session.commit()
        
        # Leave Balances (Mock)
        for u in [admin, manager, employee]:
            bal = LeaveBalance(user_id=u.id, year=2025, granted=15, remaining=15)
            db.session.add(bal)
        
        # Expense Categories
        from app.models.expense import ExpenseCategory
        cats = [
             ExpenseCategory(name="식대", code="5101"),
             ExpenseCategory(name="교통비", code="5102"),
             ExpenseCategory(name="소모품비", code="5103"),
             ExpenseCategory(name="도서비", code="5104")
        ]
        db.session.add_all(cats)
        
        db.session.commit()
    
        # 5. Default Company Info
        if not CompanyInfo.query.first():
            comp = CompanyInfo(
                company_name="주식회사 FlexLite",
                owner_name="김대표",
                registration_number="123-45-67890",
                address="서울시 강남구 테헤란로 123, 4층",
                business_type="서비스, 소프트웨어",
                business_item="시스템 통합, 유지보수",
                phone="02-1234-5678",
                email="contact@flexlite.com"
            )
            db.session.add(comp)
            db.session.commit()

        print("Seeding Complete. Admin: admin@flexlite.com / password")

if __name__ == "__main__":
    seed()
