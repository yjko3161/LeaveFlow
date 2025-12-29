from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.certificate import CertificateRequest, CertificateType
from app.services.approval_service import ApprovalService
from datetime import datetime

bp = Blueprint('certificate', __name__, url_prefix='/certificate')

@bp.route('/request', methods=['GET', 'POST'])
@login_required
def request_cert():
    if request.method == 'POST':
        cert_type = request.form.get('cert_type')
        reason = request.form.get('reason')
        issue_to = request.form.get('issue_to')
        
        cert = CertificateRequest(
            user_id=current_user.id,
            cert_type=cert_type,
            reason=reason,
            issue_to=issue_to,
            status_local="SUBMITTED"
        )
        db.session.add(cert)
        db.session.flush()
        
        # Auto-Approve or Manager Approval? 
        # Requirement: "Request -> Approval". Let's route to HR (Admin).
        from app.models.user import User
        # Find HR team member? Simplified: Admin (User 1)
        approver = User.query.get(1)
        
        service = ApprovalService()
        req = service.create_request("CERTIFICATE", cert.id, current_user.id, [approver.id])
        service.submit_request(req.id, current_user.id)
        
        flash('증명서 발급 신청이 되었습니다.', 'success')
        return redirect(url_for('certificate.list'))
        
    return render_template('certificate/form.html')

@bp.route('/')
@login_required
def list():
    certs = CertificateRequest.query.filter_by(user_id=current_user.id).order_by(CertificateRequest.created_at.desc()).all()
    return render_template('certificate/index.html', certs=certs)

@bp.route('/<int:id>/preview')
@login_required
def preview(id):
    cert = CertificateRequest.query.get_or_404(id)
    if cert.user_id != current_user.id and current_user.role != 'ADMIN':
        flash('권한이 없습니다.', 'error')
        return redirect(url_for('certificate.list'))
        
    if cert.status_local != 'APPROVED':
        flash('승인되지 않은 증명서입니다.', 'error')
        return redirect(url_for('certificate.list'))
        
    from app.models.company import CompanyInfo
    company = CompanyInfo.query.first()
    today = datetime.now()
        
    return render_template('certificate/preview.html', cert=cert, company=company, today=today)
