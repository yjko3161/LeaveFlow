from app import db, create_app
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        # Update users table
        db.session.execute(text("ALTER TABLE users ADD COLUMN department VARCHAR(100)"))
        db.session.commit()
        print("Added department to users")
    except Exception as e:
        print(f"User table error: {e}")

    try:
        # Update certificate_requests table
        db.session.execute(text("ALTER TABLE certificate_requests ADD COLUMN department VARCHAR(100)"))
        db.session.execute(text("ALTER TABLE certificate_requests ADD COLUMN issue_to VARCHAR(100)"))
        db.session.commit()
        print("Added department and issue_to to certificate_requests")
    except Exception as e:
        print(f"Cert table error: {e}")
