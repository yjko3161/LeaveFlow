from app import db, create_app
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        db.session.execute(text("ALTER TABLE certificate_requests ADD COLUMN position VARCHAR(100)"))
        db.session.commit()
        print("Added position column to certificate_requests")
    except Exception as e:
        print(f"Error: {e}")
