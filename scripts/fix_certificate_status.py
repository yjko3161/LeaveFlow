from app import create_app, db
from app.models.approval import ApprovalRequest, RequestStatus
from app.models.certificate import CertificateRequest

def fix_statuses():
    app = create_app()
    with app.app_context():
        # Find approved ApprovalRequests for Certificates
        print("Checking for out-of-sync certificates...")
        approvals = ApprovalRequest.query.filter_by(doc_type='CERTIFICATE', status=RequestStatus.APPROVED).all()
        
        count = 0
        for req in approvals:
            cert = CertificateRequest.query.get(req.doc_id)
            if cert and cert.status_local != 'APPROVED':
                print(f"Fixing Certificate #{cert.id} (Req #{req.id})")
                cert.status_local = 'APPROVED'
                count += 1
        
        if count > 0:
            db.session.commit()
            print(f"Fixed {count} certificates.")
        else:
            print("No certificates needed fixing.")

if __name__ == "__main__":
    fix_statuses()
