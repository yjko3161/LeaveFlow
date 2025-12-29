from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.approval import ApprovalRequest, ApprovalStep, RequestStatus
from app.services.approval_service import ApprovalService

bp = Blueprint('approval', __name__, url_prefix='/approval')

@bp.route('/inbox')
@login_required
def inbox():
    if current_user.role == 'ADMIN':
        # Admin sees ALL pending requests matched by badge logic
        # Badge logic: status in [SUBMITTED, IN_PROGRESS]
        requests = ApprovalRequest.query.filter(
            ApprovalRequest.status.in_([RequestStatus.SUBMITTED, RequestStatus.IN_PROGRESS])
        ).order_by(ApprovalRequest.created_at.desc()).all()
    else:
        # Find steps where I am the approver and status is PENDING
        pending_steps = ApprovalStep.query.filter_by(approver_id=current_user.id, status='PENDING').all()
        # Get associated requests
        requests = []
        for step in pending_steps:
            # verify request is technically in progress (or submitted)
            if step.request.status in [RequestStatus.SUBMITTED, RequestStatus.IN_PROGRESS]:
                 requests.append(step.request)

    # Sort by recent
    requests = sorted(requests, key=lambda x: x.created_at, reverse=True)
    
    # Attach summary info for template
    for req in requests:
        req.summary_text = ""
        if req.doc_type == "LEAVE":
            from app.models.leave import LeaveRequest
            doc = LeaveRequest.query.get(req.doc_id)
            if doc:
                req.summary_text = f"{doc.leave_type.value} ({doc.start_date.strftime('%Y.%m.%d')} ~ {doc.end_date.strftime('%Y.%m.%d')}, {doc.days}일)"
        elif req.doc_type == "EXPENSE":
             from app.models.expense import ExpenseReport
             doc = ExpenseReport.query.get(req.doc_id)
             if doc:
                 req.summary_text = f"{doc.title} ({'{:,}'.format(doc.total_amount)}원)"
        elif req.doc_type == "QUOTE":
             from app.models.quote import Quote
             doc = Quote.query.get(req.doc_id)
             if doc:
                 req.summary_text = f"{doc.title} -> {doc.client_name}"
        elif req.doc_type == "CERTIFICATE":
             from app.models.certificate import CertificateRequest
             doc = CertificateRequest.query.get(req.doc_id)
             if doc:
                 req.summary_text = f"{doc.cert_type.value} ({doc.reason})"
                 
    return render_template('approval/inbox.html', requests=requests)

@bp.route('/<int:request_id>', methods=['GET'])
@login_required
def detail(request_id):
    req = ApprovalRequest.query.get_or_404(request_id)
    # Check permission (Requester or Approver or Admin)
    # For MVP: Allow if involved
    # Load document details based on doc_type
    doc_detail = None
    if req.doc_type == "LEAVE":
        from app.models.leave import LeaveRequest
        doc_detail = LeaveRequest.query.get(req.doc_id)
    elif req.doc_type == "EXPENSE":
        from app.models.expense import ExpenseReport
        doc_detail = ExpenseReport.query.get(req.doc_id)
    elif req.doc_type == "QUOTE":
        from app.models.quote import Quote
        doc_detail = Quote.query.get(req.doc_id)
    elif req.doc_type == "CERTIFICATE":
        from app.models.certificate import CertificateRequest
        doc_detail = CertificateRequest.query.get(req.doc_id)
        
    return render_template('approval/detail.html', req=req, doc=doc_detail)

@bp.route('/<int:request_id>/action', methods=['POST'])
@login_required
def action(request_id):
    action_type = request.form.get('action') # APPROVE, REJECT
    comment = request.form.get('comment')
    
    service = ApprovalService()
    if action_type == 'APPROVE':
        success, msg = service.approve_step(request_id, current_user.id, comment)
    elif action_type == 'REJECT':
        success, msg = service.reject_step(request_id, current_user.id, comment)
    else:
        success, msg = False, "Invalid action"
        
    if success:
        flash(f'성공적으로 처리되었습니다: {action_type}', 'success')
        return redirect(url_for('approval.inbox'))
    else:
        flash(f'처리 실패: {msg}', 'error')
        return redirect(url_for('approval.detail', request_id=request_id))
