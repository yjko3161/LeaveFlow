from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.company import CompanyInfo

bp = Blueprint('settings', __name__, url_prefix='/settings')

@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        # Change Password
        pwd = request.form.get('password')
        confirm = request.form.get('confirm')
        
        if pwd:
            if pwd == confirm:
                current_user.set_password(pwd)
                flash('비밀번호가 변경되었습니다.', 'success')
            else:
                flash('비밀번호가 일치하지 않습니다.', 'error')
        
        # Update Card Number
        card_num = request.form.get('card_number')
        if card_num is not None:
            current_user.card_number = card_num
            flash('개인 정보가 수정되었습니다.', 'success')
            
        db.session.commit()
    
    # Get Signature
    from app.models.user import UserSignature
    sig = UserSignature.query.filter_by(user_id=current_user.id).first()
    signature_url = None
    if sig and sig.image_path:
        # Assuming we have a route to serve uploads, or static
        # Let's say we serve uploads via /uploads/
        # Need to check if a route exists for serving uploads.
        # Usually it's handled by Nginx or a special route.
        # Let's assume we add a route in main.py or similar
        signature_url = url_for('main.uploaded_file', filename=sig.image_path)
        
    return render_template('settings/index.html', signature_url=signature_url)

@bp.route('/company', methods=['GET', 'POST'])
@login_required
def company():
    if current_user.role not in ['ADMIN', 'MANAGER']: # Allow Manager? User said "Admin only" for access control before. Let's stick to base.html logic (Admin/Manager link) but strict Admin check here?
        # User request: "Company Info Settings tab... only this content"
        # Previous logic was Admin only.
        if current_user.role != 'ADMIN':
             flash('권한이 없습니다.', 'error')
             return redirect(url_for('settings.index'))

    company = CompanyInfo.query.first()
    if not company:
        company = CompanyInfo() # Empty for form

    if request.method == 'POST':
        if not company.id:
            db.session.add(company)
        
        company.company_name = request.form.get('company_name')
        company.owner_name = request.form.get('owner_name')
        company.registration_number = request.form.get('registration_number')
        company.address = request.form.get('address')
        company.business_type = request.form.get('business_type')
        company.business_item = request.form.get('business_item')
        company.phone = request.form.get('phone')
        
        # Handle Seal Upload
        file = request.files.get('stamp_file')
        if file and file.filename != '':
            import os
            from werkzeug.utils import secure_filename
            from flask import current_app
            import time
            
            filename = secure_filename(f"stamp_{int(time.time())}.png")
            sig_dir = os.path.join(current_app.config['UPLOAD_DIR'], 'signatures')
            os.makedirs(sig_dir, exist_ok=True)
            
            filepath = os.path.join(sig_dir, filename)
            file.save(filepath)
            
            # Save path (relative to upload dir)
            company.stamp_path = f"signatures/{filename}"

        db.session.commit()
        flash('회사 정보가 수정되었습니다.', 'success')
        return redirect(url_for('settings.company'))

    return render_template('settings/company.html', company=company)

@bp.route('/signature', methods=['POST'])
@login_required
def upload_signature():
    if 'signature' not in request.files:
        flash('파일이 없습니다.', 'error')
        return redirect(url_for('settings.index'))
        
    file = request.files['signature']
    if file.filename == '':
        flash('선택된 파일이 없습니다.', 'error')
        return redirect(url_for('settings.index'))
        
    if file:
        import os
        from werkzeug.utils import secure_filename
        from flask import current_app
        
        filename = secure_filename(f"sig_{current_user.id}_{int(os.path.getmtime(os.path.join(current_app.config['UPLOAD_DIR'])) if os.path.exists(current_app.config['UPLOAD_DIR']) else 0)}.png") # Simple unique name
        # Better: use timestamp
        import time
        filename = secure_filename(f"sig_{current_user.id}_{int(time.time())}.png")
        
        # Ensure dir
        sig_dir = os.path.join(current_app.config['UPLOAD_DIR'], 'signatures')
        os.makedirs(sig_dir, exist_ok=True)
        
        filepath = os.path.join(sig_dir, filename)
        file.save(filepath)
        
        # Update DB
        from app.models.user import UserSignature, SignatureType
        
        sig = UserSignature.query.filter_by(user_id=current_user.id).first()
        if not sig:
            sig = UserSignature(user_id=current_user.id)
            db.session.add(sig)
            
        sig.signature_type = SignatureType.STAMP_IMAGE
        sig.image_path = f"signatures/{filename}"
        
        db.session.commit()
        flash('서명이 등록되었습니다.', 'success')
        
    return redirect(url_for('settings.index'))
