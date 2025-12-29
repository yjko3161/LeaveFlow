from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models.expense import ExpenseCategory, ExpenseReceipt, ExpenseReport
from app.models.file import File
from app.services.approval_service import ApprovalService
from datetime import datetime
import os
from werkzeug.utils import secure_filename

bp = Blueprint('expense', __name__, url_prefix='/expense')

@bp.route('/')
@login_required
def index():
    # Show my reports
    reports = ExpenseReport.query.filter_by(user_id=current_user.id).order_by(ExpenseReport.created_at.desc()).all()
    # Show unsubmitted receipts
    receipts = ExpenseReceipt.query.filter_by(user_id=current_user.id, report_id=None).all()
    categories = ExpenseCategory.query.all()
    today_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('expense/index.html', reports=reports, receipts=receipts, categories=categories, today_date=today_date)

@bp.route('/receipt/new', methods=['POST'])
@login_required
def new_receipt():
    merchant = request.form.get('merchant')
    amount = request.form.get('amount')
    date_str = request.form.get('usage_date')
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
    category_id = request.form.get('category_id')
    desc = request.form.get('description')
    
    # File Upload
    file = request.files.get('receipt_file')
    file_record = None
    if file and file.filename:
        filename = secure_filename(file.filename)
        path = os.path.join(current_app.config['UPLOAD_DIR'], filename)
        # Ensure dir exists
        os.makedirs(current_app.config['UPLOAD_DIR'], exist_ok=True)
        file.save(path)
        
        file_record = File(filename=filename, filepath=path, uploaded_by=current_user.id)
        db.session.add(file_record)
        db.session.flush()
    
    receipt = ExpenseReceipt(
        user_id=current_user.id,
        category_id=category_id,
        usage_date=datetime.strptime(date_str, '%Y-%m-%d').date(),
        merchant=merchant,
        amount=int(amount),
        description=desc,
        file_id=file_record.id if file_record else None
    )
    db.session.add(receipt)
    db.session.commit()
    
    flash('영수증이 등록되었습니다.', 'success')
    return redirect(url_for('expense.index'))

@bp.route('/report/new', methods=['POST'])
@login_required
def new_report():
    title = request.form.get('title')
    receipt_ids = request.form.getlist('receipt_ids')
    
    if not receipt_ids:
        flash('선택된 영수증이 없습니다.', 'error')
        return redirect(url_for('expense.index'))
    
    # Create Report
    report = ExpenseReport(
        user_id=current_user.id,
        title=title,
        status_local="SUBMITTED"
    )
    db.session.add(report)
    db.session.flush()
    
    total = 0
    for rid in receipt_ids:
        r = ExpenseReceipt.query.get(rid)
        if r and r.user_id == current_user.id:
            r.report_id = report.id
            total += r.amount
            
    report.total_amount = total
    
    # Approval
    approver = current_user.team.manager
    if not approver:
        from app.models.user import User
        approver = User.query.get(1) # Admin fallback
        
    service = ApprovalService()
    req = service.create_request("EXPENSE", report.id, current_user.id, [approver.id])
    service.submit_request(req.id, current_user.id)
    
    flash('지출결의서가 제출되었습니다.', 'success')
    return redirect(url_for('expense.index'))

@bp.route('/report/<int:id>')
@login_required
def detail(id):
    report = ExpenseReport.query.get_or_404(id)
    # Check permission (User's own or Admin/Manager)
    if report.user_id != current_user.id and current_user.role not in ['ADMIN', 'MANAGER']:
        flash('권한이 없습니다.', 'error')
        return redirect(url_for('expense.index'))
    
    # Fetch Approval Info
    from app.models.approval import ApprovalRequest
    approval = ApprovalRequest.query.filter_by(doc_type='EXPENSE', doc_id=id).order_by(ApprovalRequest.created_at.desc()).first()
        
    return render_template('expense/detail.html', report=report, approval=approval)
