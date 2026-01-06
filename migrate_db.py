from app import create_app, db
import os
from dotenv import load_dotenv

load_dotenv()

app = create_app()

def migrate():
    with app.app_context():
        # Explicitly import all models to ensure they are registered with SQLAlchemy metadata
        from app.models import user, approval, leave, expense, certificate, quote, company, stamp
        
        print(f"Connecting to: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Check what tables SQLAlchemy knows about
        print("Tables detected in metadata:")
        for table in db.metadata.tables.keys():
            print(f" - {table}")
            
        print("\nCreating new tables (if not exists)...")
        db.create_all()
        
        # Verify if tables now exist (SQLAlchemy view)
        print("\nTables in metadata after create_all:")
        for table in db.metadata.tables.keys():
            print(f" - {table}")
            
        print("\nMigration Complete.")

if __name__ == "__main__":
    migrate()
