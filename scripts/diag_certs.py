from app import create_app, db
from app.models.certificate import CertificateRequest

def diag():
    app = create_app()
    with app.app_context():
        certs = CertificateRequest.query.all()
        print(f"Total Certs: {len(certs)}")
        for c in certs:
            print(f"ID: {c.id}, Type: {c.cert_type}, Status: '{c.status_local}', Reason: {c.reason}")

if __name__ == "__main__":
    diag()
