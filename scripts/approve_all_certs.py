from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.models.approval import ApprovalRequest, RequestStatus
from app.models.certificate import CertificateRequest

def approve_all():
    app = create_app()
    with app.app_context():
        # Approve all pending/submitted certificates
        # Use simple string match since status_local is a Column(String) usually
        certs = CertificateRequest.query.filter(CertificateRequest.status_local.in_(['SUBMITTED', 'PENDING'])).all()
        print(f"Found {len(certs)} pending certificates.")
        for c in certs:
            print(f"Approve Cert #{c.id}")
            c.status_local = 'APPROVED'
            # Also approve the associated ApprovalRequest so it looks consistent in Dashboards
            req = ApprovalRequest.query.filter_by(doc_type='CERTIFICATE', doc_id=c.id).first()
            if req:
                req.status = RequestStatus.APPROVED
                for s in req.steps:
                    s.status = 'APPROVED'
        
        db.session.commit()
        print(f"Approved {len(certs)} certificates.")

if __name__ == "__main__":
    approve_all()
