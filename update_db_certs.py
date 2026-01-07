from app import db, create_app
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        # Add resident_reg_number to users table
        db.session.execute(text("ALTER TABLE users ADD COLUMN resident_reg_number VARCHAR(20)"))
        print("Added resident_reg_number to users")
    except Exception as e:
        print(f"User RRN error: {e}")

    try:
        # Add address to users table
        db.session.execute(text("ALTER TABLE users ADD COLUMN address VARCHAR(255)"))
        print("Added address to users")
    except Exception as e:
        print(f"User Address error: {e}")

    try:
        # Add snapshot fields to certificate_requests table
        db.session.execute(text("ALTER TABLE certificate_requests ADD COLUMN name VARCHAR(100)"))
        db.session.execute(text("ALTER TABLE certificate_requests ADD COLUMN resident_reg_number VARCHAR(20)"))
        db.session.execute(text("ALTER TABLE certificate_requests ADD COLUMN address VARCHAR(255)"))
        db.session.execute(text("ALTER TABLE certificate_requests ADD COLUMN join_date DATE"))
        print("Added snapshot fields to certificate_requests")
    except Exception as e:
        print(f"Cert snapshot error: {e}")

    db.session.commit()
    print("Database update complete.")
