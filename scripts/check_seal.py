from app import create_app, db
from app.models.company import CompanyInfo
from app.models.quote import Quote

def check():
    app = create_app()
    with app.app_context():
        comp = CompanyInfo.query.first()
        if comp:
            print(f"Company Seal Path: {comp.stamp_path}")
        else:
            print("No CompanyInfo found.")

        q = Quote.query.get(5)
        if q:
            print(f"Quote #5 Provider Stamp Path: {q.provider_stamp_path}")
        else:
            print("Quote #5 not found.")

if __name__ == "__main__":
    check()
