from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.leave import LeaveRequest, LeaveType, LeaveBalance
from app.services.approval_service import ApprovalService
from datetime import datetime

bp = Blueprint('leave', __name__, url_prefix='/leave')

@bp.route('/')
@login_required
def index():
    requests = LeaveRequest.query.filter_by(user_id=current_user.id).order_by(LeaveRequest.created_at.desc()).all()
    return render_template('leave/index.html', requests=requests)

@bp.route('/manage')
@login_required
def manage():
    if current_user.role not in ['ADMIN', 'MANAGER']:
        flash('권한이 없습니다.', 'error')
        return redirect(url_for('leave.index'))
        
    from app.models.user import User, UserRole
    # Manager sees own team, Admin sees all
    if current_user.role == 'ADMIN':
        users = User.query.all()
    else:
        # Check if user manages a team
        team = current_user.managed_team
        if team:
            users = User.query.filter_by(team_id=team.id).all()
        else:
            users = []
            
    # balances
    balances = {}
    for u in users:
        bal = LeaveBalance.query.filter_by(user_id=u.id, year=2025).first()
        balances[u.id] = bal
        
    return render_template('leave/manage.html', users=users, balances=balances)

@bp.route('/manage/<int:user_id>/update', methods=['POST'])
@login_required
def update_balance(user_id):
    if current_user.role not in ['ADMIN', 'MANAGER']:
        flash('권한이 없습니다.', 'error')
        return redirect(url_for('leave.index'))
        
    granted = request.form.get('granted', type=int)
    remaining = request.form.get('remaining', type=int)
    
    bal = LeaveBalance.query.filter_by(user_id=user_id, year=2025).first()
    if not bal:
        bal = LeaveBalance(user_id=user_id, year=2025, granted=granted, remaining=remaining)
        db.session.add(bal)
    else:
        bal.granted = granted
        bal.remaining = remaining
        
    db.session.commit()
    flash('연차 정보가 수정되었습니다.', 'success')
    return redirect(url_for('leave.manage'))

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_request():
    if request.method == 'POST':
        leave_type = request.form.get('leave_type')
        start_str = request.form.get('start_date')
        end_str = request.form.get('end_date')
        reason = request.form.get('reason')
        
        start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
        days = (end_date - start_date).days + 1 # Simple logic
        
        # Create Leave Request
        leave_req = LeaveRequest(
            user_id=current_user.id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            days=days,
            reason=reason,
            status_local="SUBMITTED" # Optimistic
        )
        db.session.add(leave_req)
        db.session.flush()
        
        # Determine Approver (Manager)
        approver = current_user.team.manager
        if not approver:
             # Fallback to Admin?
             # For MVP, assume User #1 (Admin)
             from app.models.user import User
             approver = User.query.get(1)
        
        # Create Approval Chain
        service = ApprovalService()
        approval_req = service.create_request("LEAVE", leave_req.id, current_user.id, [approver.id])
        service.submit_request(approval_req.id, current_user.id)
        
        flash('연차 신청이 완료되었습니다.', 'success')
        return redirect(url_for('leave.index'))
        
    return render_template('leave/form.html')
