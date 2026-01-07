from app import db, create_app
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        # Update users table
        db.session.execute(text("ALTER TABLE users ADD COLUMN position VARCHAR(100)"))
        db.session.commit()
        print("Added position to users")
    except Exception as e:
        print(f"User table error: {e}")
