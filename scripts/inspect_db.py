from app import create_app, db
from app.models.approval import ApprovalRequest
from app.models.certificate import CertificateRequest

def inspect():
    app = create_app()
    with app.app_context():
        print("--- Certificate Requests ---")
        certs = CertificateRequest.query.all()
        for c in certs:
            print(f"Cert #{c.id}: StatusLocal={c.status_local}, Type={c.cert_type}")
            
        print("\n--- Approval Requests (Certificate) ---")
        reqs = ApprovalRequest.query.filter_by(doc_type='CERTIFICATE').all()
        for r in reqs:
            print(f"Req #{r.id} for Cert #{r.doc_id}: Status={r.status}, Steps={len(r.steps)}")
            for s in r.steps:
                print(f"  - Step {s.step_order}: Approver={s.approver.name}, Status={s.status}")

if __name__ == "__main__":
    inspect()
