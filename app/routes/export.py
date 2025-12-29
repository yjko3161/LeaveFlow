from flask import Blueprint, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
from app.services.export_service import ExportService

bp = Blueprint('export', __name__, url_prefix='/export')

@bp.route('/<int:request_id>')
@login_required
def download(request_id):
    service = ExportService()
    path, filename = service.generate_document(request_id)
    
    if not path:
        flash(filename, 'error') # error msg
        return redirect(url_for('approval.detail', request_id=request_id))
        
    return send_file(path, as_attachment=True, download_name=filename)
