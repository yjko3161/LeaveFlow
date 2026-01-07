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
        name = request.form.get('name')
        rrn = request.form.get('rrn')
        address = request.form.get('address')
        join_date_str = request.form.get('join_date')
        position = request.form.get('position') # Used for 'Rank/직급'
        department = request.form.get('department')
        reason = request.form.get('reason')
        issue_to = request.form.get('issue_to')
        
        join_date = None
        if join_date_str:
            join_date = datetime.strptime(join_date_str, '%Y-%m-%d').date()
            
        cert = CertificateRequest(
            user_id=current_user.id,
            cert_type=cert_type,
            name=name,
            resident_reg_number=rrn,
            address=address,
            department=department,
            position=position,
            join_date=join_date,
            reason=reason,
            issue_to=issue_to,
            status_local="SUBMITTED"
        )
        
        # Persist profile information if provided/changed
        if name and current_user.name != name:
            current_user.name = name
        if rrn and not current_user.resident_reg_number:
            current_user.resident_reg_number = rrn
        if address and not current_user.address:
            current_user.address = address
        if department and not current_user.department:
            current_user.department = department
        if position and not current_user.position:
            current_user.position = position
        if join_date and not current_user.join_date:
            current_user.join_date = join_date
            
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
    today = datetime.now().date()
    
    j_date = cert.join_date or cert.user.join_date
    duration = ""
    if j_date:
        years = today.year - j_date.year
        months = today.month - j_date.month
        if today.day < j_date.day:
            months -= 1
        if months < 0:
            years -= 1
            months += 12
        duration = f"({years}년{months}개월)"
        
    return render_template('certificate/preview.html', cert=cert, company=company, today=today, duration=duration)
