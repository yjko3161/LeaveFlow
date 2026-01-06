from app import create_app, db
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv()

app = create_app()

def check_db():
    with app.app_context():
        print(f"Checking DB: {app.config['SQLALCHEMY_DATABASE_URI']}")
        try:
            result = db.session.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result]
            print("Tables in Database:")
            for t in tables:
                print(f" - {t}")
                
            if 'stamp_assets' in tables:
                print("\nSUCCESS: 'stamp_assets' exists!")
            else:
                print("\nFAILURE: 'stamp_assets' DOES NOT exist in the database.")
                
        except Exception as e:
            print(f"Error checking DB: {e}")

if __name__ == "__main__":
    check_db()
