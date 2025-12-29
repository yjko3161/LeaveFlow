from app import create_app, db
from app.models.company import CompanyInfo
from app.models.quote import Quote
from dotenv import load_dotenv

def backfill():
    load_dotenv()
    app = create_app()
    with app.app_context():
        comp = CompanyInfo.query.first()
        if not comp or not comp.stamp_path:
            print("No company seal found to backfill.")
            return

        # Backfill all quotes where provider_stamp_path is NULL or empty
        from sqlalchemy import or_
        quotes = Quote.query.filter(or_(Quote.provider_stamp_path == None, Quote.provider_stamp_path == '')).all()
        count = 0
        for q in quotes:
            print(f"Backfilling Quote #{q.id} with seal: {comp.stamp_path}")
            q.provider_stamp_path = comp.stamp_path
            count += 1
        
        if count > 0:
            db.session.commit()
            print(f"Success: Backfilled {count} quotes.")
        else:
            print("No quotes needed backfilling.")

if __name__ == "__main__":
    backfill()
