from app import db
from app.models.approval import ApprovalRequest, ApprovalStep, ApprovalAction, RequestStatus
from app.models.user import User
from datetime import datetime

class ApprovalService:
    def create_request(self, doc_type, doc_id, requester_id, approver_ids):
        """
        Create a new approval request with steps.
        approver_ids: List of user_ids for sequential approval steps.
        """
        request = ApprovalRequest(
            doc_type=doc_type,
            doc_id=doc_id,
            requester_id=requester_id,
            status=RequestStatus.DRAFT
        )
        db.session.add(request)
        db.session.flush() # get ID
        
        for idx, uid in enumerate(approver_ids):
            step = ApprovalStep(
                request_id=request.id,
                step_order=idx + 1,
                approver_id=uid,
                status="PENDING"
            )
            db.session.add(step)
            
        db.session.commit()
        return request

    def submit_request(self, request_id, actor_id):
        request = ApprovalRequest.query.get(request_id)
        if not request:
            return False, "Request not found"
        
        if request.status != RequestStatus.DRAFT and request.status != RequestStatus.REJECTED:
             # Retry submission allowed if rejected? User spec says "Rejected -> Edit -> Submit"
             # So status might need to go back to SUBMITTED.
             pass
        
        # Check integrity??
        request.status = RequestStatus.SUBMITTED
        request.current_step_order = 1
        
        # Reset steps if re-submitting?
        for step in request.steps:
            step.status = "PENDING"
            
        self._log_action(request.id, None, actor_id, "SUBMIT")
        db.session.commit()
        
        # Notify first approver
        # send_email(...)
        
        request.status = RequestStatus.IN_PROGRESS
        db.session.commit()
        
        return True, "Submitted"

    def approve_step(self, request_id, actor_id, comment=None):
        request = ApprovalRequest.query.get(request_id)
        current_step = next((s for s in request.steps if s.step_order == request.current_step_order), None)
        
        if not current_step:
            return False, "Invalid step"
            
        # Auth Check
        actor = User.query.get(actor_id)
        if current_step.approver_id != actor_id and actor.role != 'ADMIN':
            return False, "Not authorized"
            
        current_step.status = "APPROVED"
        # If Admin approved on behalf of someone else, maybe note that?
        self._log_action(request.id, current_step.id, actor_id, "APPROVE", comment)
        
        # Move to next
        next_step = next((s for s in request.steps if s.step_order > request.current_step_order and s.status == "PENDING"), None)
        
        if next_step:
            request.current_step_order = next_step.step_order
            # Notify next
        else:
            # Check if there are ANY pending steps left (safety)
            has_pending = any(s.status == "PENDING" for s in request.steps)
            if not has_pending:
                # Final Approval
                request.status = RequestStatus.APPROVED
                # Trigger Lock / Finalize logic (Callback?)
                self._finalize_document(request)
            else:
                # This might happen if steps are out of order, move order to the first pending
                first_pending = sorted([s for s in request.steps if s.status == "PENDING"], key=lambda x: x.step_order)[0]
                request.current_step_order = first_pending.step_order
            
        db.session.commit()
        return True, "Approved"

    def reject_step(self, request_id, actor_id, comment=None):
        request = ApprovalRequest.query.get(request_id)
        current_step = next((s for s in request.steps if s.step_order == request.current_step_order), None)
        
        # Auth Check
        actor = User.query.get(actor_id)
        if not current_step or (current_step.approver_id != actor_id and actor.role != 'ADMIN'):
             return False, "Not authorized"
             
        current_step.status = "REJECTED"
        request.status = RequestStatus.REJECTED
        self._log_action(request.id, current_step.id, actor_id, "REJECT", comment)
        
        db.session.commit()
        return True, "Rejected"

    def _log_action(self, req_id, step_id, actor_id, action, comment=None):
        log = ApprovalAction(
            request_id=req_id,
            step_id=step_id,
            actor_id=actor_id,
            action=action,
            comment=comment
        )
        db.session.add(log)

    def _finalize_document(self, request):
        """
        Callback to lock the target document (Leave, Expense, etc.)
        """
        if request.doc_type == "LEAVE":
            from app.models.leave import LeaveRequest, LeaveBalance
            doc = LeaveRequest.query.get(request.doc_id)
            if doc and doc.status_local != "APPROVED":
                doc.status_local = "APPROVED"
                
                # Check for insufficient balance?? Validation should happen at Request time, but check again?
                # For now, just deduct.
                # Find balance record year
                year = doc.start_date.year
                balance = LeaveBalance.query.filter_by(user_id=request.requester_id, year=year).first()
                if balance:
                    balance.used = (balance.used or 0) + doc.days
                    balance.remaining = (balance.remaining or 0) - doc.days
                    # if balance.remaining < 0: Warn? Allow negative? 
                    # ERP typically allows negative if authorized.
        elif request.doc_type == "EXPENSE":
            from app.models.expense import ExpenseReport
            doc = ExpenseReport.query.get(request.doc_id)
            if doc:
                doc.status_local = "APPROVED"
        elif request.doc_type == "CERTIFICATE":
            from app.models.certificate import CertificateRequest
            doc = CertificateRequest.query.get(request.doc_id)
            if doc:
                doc.status_local = "APPROVED"
        # ...
