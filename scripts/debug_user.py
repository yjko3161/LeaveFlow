from app import create_app
from app.models.user import User

app = create_app()
with app.app_context():
    u = User.query.filter_by(email="employee@flexlite.com").first()
    if u:
        print(f"User found: {u.id}, {u.email}, Hash: {u.password_hash}")
        print(f"Check 'password': {u.check_password('password')}")
    else:
        print("User NOT found")
