from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime
from app import db
from app.models.user import User, UserRole
from app.models.leave import LeaveBalance
from app.models.approval import ApprovalRequest, RequestStatus
from app.models.expense import ExpenseReport

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def dashboard():
    today = datetime.today()
    current_year = today.year
    current_month = today.month

    # Defaults
    leave_remaining = 0
    leave_total = 0
    pending_approvals_count = 0
    monthly_expenses = 0

    # Common: Recent Activity (Last 5)
    # Filter by user if not admin? User said "Recent Approvals".
    # Usually Dashboard shows what's relevant to the user.
    # If Admin, maybe see all? If Employee, see own?
    # User said "Recent approval history shows old content".
    # Let's show:
    # - For Admin: All Key Actions
    # - For Employee: My Requests & Requests waiting for me
    
    recent_activities = []
    all_users_leave = []

    if current_user.role == UserRole.ADMIN:
        # 1. Leave Stats (Existing logic) - Keep for Top Cards (Totals)
        leave_stats = db.session.query(
            func.sum(LeaveBalance.remaining),
            func.sum(LeaveBalance.granted)
        ).filter(LeaveBalance.year == current_year).first()
        leave_remaining = leave_stats[0] or 0
        leave_total = leave_stats[1] or 0

        # ... (Existing Pending Approvals & Expenses logic) ...

        # NEW: Filter Pending Approvals (Status is PENDING)
        pending_approvals_count = ApprovalRequest.query.filter_by(status=RequestStatus.IN_PROGRESS).count() # PENDING is not in RequestStatus, IN_PROGRESS or SUBMITTED? 
        # Check RequestStatus: DRAFT, SUBMITTED, IN_PROGRESS, APPROVED, REJECTED, CANCELLED.
        # "Pending" for Admin implies "Submitted" or "In Progress" waiting for approval. 
        # For simplicity, let's count SUBMITTED & IN_PROGRESS
        pending_approvals_count = ApprovalRequest.query.filter(ApprovalRequest.status.in_([RequestStatus.SUBMITTED, RequestStatus.IN_PROGRESS])).count()
        
        # NEW: Monthly Expenses (Approved)
        monthly_expenses = db.session.query(func.sum(ExpenseReport.total_amount))\
            .join(ApprovalRequest, (ApprovalRequest.doc_type == 'EXPENSE') & (ApprovalRequest.doc_id == ExpenseReport.id))\
            .filter(
                func.extract('year', ExpenseReport.created_at) == current_year,
                func.extract('month', ExpenseReport.created_at) == current_month,
                ApprovalRequest.status == RequestStatus.APPROVED
            ).scalar() or 0

        # NEW: Fetch All Users Leave Data for Table
        # Join User and LeaveBalance (Outer join in case no balance)
        all_users_leave = db.session.query(
            User.name, 
            LeaveBalance.granted, 
            LeaveBalance.used, 
            LeaveBalance.remaining
        ).outerjoin(LeaveBalance, (User.id == LeaveBalance.user_id) & (LeaveBalance.year == current_year))\
         .filter(User.role != UserRole.ADMIN).all() # Exclude Admin from list? Or keep. User said "Employee specs".
         
        # Recent Activities: All latest requests
        recent_activities = ApprovalRequest.query.order_by(ApprovalRequest.created_at.desc()).limit(5).all()

    else:
        # Employee Logic (Existing)
        my_balance = LeaveBalance.query.filter_by(user_id=current_user.id, year=current_year).first()
        if my_balance:
            leave_remaining = my_balance.remaining
            leave_total = my_balance.granted
        
        pending_approvals_count = ApprovalRequest.query.filter(
            ApprovalRequest.requester_id == current_user.id,
            ApprovalRequest.status.in_([RequestStatus.SUBMITTED, RequestStatus.IN_PROGRESS])
        ).count()

        monthly_expenses = db.session.query(func.sum(ExpenseReport.total_amount))\
            .join(ApprovalRequest, (ApprovalRequest.doc_type == 'EXPENSE') & (ApprovalRequest.doc_id == ExpenseReport.id))\
            .filter(
                ExpenseReport.user_id == current_user.id,
                func.extract('year', ExpenseReport.created_at) == current_year,
                func.extract('month', ExpenseReport.created_at) == current_month,
                ApprovalRequest.status == RequestStatus.APPROVED
            ).scalar() or 0
            
        # Recent Activities: My Requests
        recent_activities = ApprovalRequest.query.filter_by(requester_id=current_user.id)\
            .order_by(ApprovalRequest.created_at.desc()).limit(5).all()

    # NEW: Approved Leaves for This Month (Visible to Everyone)
    from app.models.leave import LeaveRequest
    from datetime import date
    
    # Simple overlap check: start_date <= last_day AND end_date >= first_day
    # Or just start in this month? User said "Applicants who are approved for this month". implies presence.
    # Let's show leaves starting in this month.
    
    approved_leaves_this_month = LeaveRequest.query.filter(
        func.extract('year', LeaveRequest.start_date) == current_year,
        func.extract('month', LeaveRequest.start_date) == current_month,
        LeaveRequest.status_local == 'APPROVED'
    ).all()

    return render_template(
        'dashboard.html',
        leave_remaining=leave_remaining,
        leave_total=leave_total,
        pending_approvals_count=pending_approvals_count,
        monthly_expenses=monthly_expenses,
        current_year=current_year,
        current_month=current_month,
        recent_activities=recent_activities,
        all_users_leave=all_users_leave,
        approved_leaves_this_month=approved_leaves_this_month
    )

@bp.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename):
    from flask import send_from_directory, current_app
    import os
    return send_from_directory(current_app.config['UPLOAD_DIR'], filename)
