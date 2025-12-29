from app import create_app, db
from app.models.user import User
from flask_login import login_user

app = create_app()

def test_dashboard_load():
    with app.app_context():
        # Test Admin Dashboard
        admin = User.query.filter_by(role='ADMIN').first()
        if not admin:
            print("No admin user found")
            return

        with app.test_request_context('/'):
            # Mock login
            login_user(admin)
            from app.routes.main import dashboard
            print("Loading Admin Dashboard...")
            try:
                response = dashboard()
                print("[SUCCESS] Admin Dashboard Loaded")
            except Exception as e:
                print(f"[ERROR] Admin Dashboard Failed: {e}")
                import traceback
                traceback.print_exc()

        # Test Employee Dashboard
        emp = User.query.filter_by(role='EMPLOYEE').first()
        if emp:
            with app.test_request_context('/'):
                login_user(emp)
                print("Loading Employee Dashboard...")
                try:
                    dashboard()
                    print("[SUCCESS] Employee Dashboard Loaded")
                except Exception as e:
                    print(f"[ERROR] Employee Dashboard Failed: {e}")
        else:
            print("No employee user found")

if __name__ == "__main__":
    test_dashboard_load()
