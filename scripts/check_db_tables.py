from app import create_app, db
from sqlalchemy import inspect

app = create_app()

def check_tables():
    with app.app_context():
        print(f"Checking DB: {app.config['SQLALCHEMY_DATABASE_URI']}")
        # Force connection check
        try:
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print("--- Database Tables ---")
            for table in tables:
                print(f"- {table}")
            print(f"Total Tables: {len(tables)}")
            
            if 'users' in tables and 'quotes' in tables and 'company_info' in tables:
                print("[SUCCESS] Core tables found.")
            else:
                print("[WARNING] Some core tables are missing.")
                
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")

if __name__ == "__main__":
    check_tables()
