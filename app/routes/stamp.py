from flask import Blueprint, render_template, request, jsonify, current_app, send_from_directory
from flask_login import login_required, current_user
from app.services.stamp_service import StampService
from app.models.stamp import StampAsset, StampAssetType
from app import db
import os
import uuid

bp = Blueprint('stamp', __name__, url_prefix='/stamp')

@bp.route('/')
@login_required
def index():
    return render_template('stamps/manage.html')

@bp.route('/preview')
@login_required
def preview():
    text = request.args.get('text', '')
    group = request.args.get('type', 'general')
    lang = request.args.get('lang', 'ko')

    if not text:
        return '<div class="alert alert-warning">텍스트를 입력해주세요.</div>'
    
    if len(text) > 20:
        return '<div class="alert alert-danger">텍스트가 너무 깁니다. (최대 20자)</div>'

    # Get presets from StampService
    presets = StampService.get_default_templates()
    # Filter by group if needed
    filtered_presets = [p for p in presets if p['group'] == group]

    # STYLES to generate variations for (mimicking Donue)
    # If user selected a specific one, use it. If not (or 'all'), generate all.
    req_style = request.args.get('font_style', 'all')
    
    styles = ['batang', 'gungsuh', 'jeonseo', 'goinche', 'choseo', 'dotum']
    if req_style and req_style != 'all':
        styles = [req_style]

    previews = []
    for preset in filtered_presets:
        # For each preset, generate variations for each font style
        for style in styles:
            # Create a copy of the spec to avoid mutating the original preset
            spec = preset['spec'].copy()
            spec['font_style'] = style
            
            svg_content = StampService.generate_svg(text, spec, group)
            
            # Label the preview helper
            style_label = {
                'batang': '명조체', 'gungsuh': '궁서체', 'jeonseo': '전서체',
                'goinche': '고인체', 'choseo': '초서체', 'dotum': '고딕체'
            }.get(style, style)
            
            previews.append({
                'code': preset['code'], # Note: Keeping same code might be issue for saving, need to encode style?
                # Actually, we should probably encode style into the code or pass it separately.
                # For now, let's append it to code so save() can parse it?
                # Or just pass 'spec' to save... current save() re-generates from preset['code'].
                # We need to hack save() to accept font_style override. 
                # Let's append style to code like "corp_circular:jeonseo"
                'code': f"{preset['code']}:{style}", 
                'svg': svg_content,
                'label': f"{preset.get('name', '')} - {style_label}"
            })

    return render_template('stamps/preview_grid.html', previews=previews, text=text, group=group)

@bp.route('/save', methods=['POST'])
@login_required
def save():
    data = request.json
    template_code = data.get('template_code')
    text = data.get('text')
    group = data.get('group')

    if not text or not template_code:
        return jsonify({'status': 'error', 'message': 'Missing data'}), 400

    # Find template spec
    # Handle 'code:style' format from multi-font preview
    font_style_override = None
    real_code = template_code
    if ':' in template_code:
        real_code, font_style_override = template_code.split(':')

    presets = StampService.get_default_templates()
    preset = next((p for p in presets if p['code'] == real_code), None)
    
    if not preset:
        return jsonify({'status': 'error', 'message': 'Invalid template'}), 400

    # Apply style override if present
    spec = preset['spec'].copy()
    if font_style_override:
        spec['font_style'] = font_style_override

    svg_content = StampService.generate_svg(text, spec, group)
    
    # Save files
    filename_base = f"{uuid.uuid4()}"
    upload_subdir = 'stamps' if group != 'sign' else 'signatures'
    save_dir = os.path.join(current_app.config['UPLOAD_DIR'], upload_subdir)
    os.makedirs(save_dir, exist_ok=True)
    
    svg_path = os.path.join(save_dir, f"{filename_base}.svg")
    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    # Create Asset
    asset_type = StampAssetType.STAMP if group != 'sign' else StampAssetType.SIGN
    asset = StampAsset(
        user_id=current_user.id,
        type=asset_type,
        template_code=template_code,
        text=text,
        file_svg_path=f"{upload_subdir}/{filename_base}.svg"
    )
    db.session.add(asset)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'asset_id': asset.id,
        'svg_path': asset.file_svg_path
    })

@bp.route('/list')
@login_required
def list_assets():
    assets = StampAsset.query.filter_by(user_id=current_user.id).order_by(StampAsset.created_at.desc()).all()
    return render_template('stamps/asset_list.html', assets=assets)
@bp.route('/download/<int:asset_id>')
@login_required
def download(asset_id):
    asset = StampAsset.query.get_or_404(asset_id)
    if asset.user_id != current_user.id:
        return "Unauthorized", 403
    
    import io
    import re
    from flask import send_file
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    # 1. Register Standard Korean System Fonts
    # Prioritize Malgun Gothic (TTF) as it is most stable for ReportLab on Windows
    # We must register Bold variant to handle font-weight="bold" correctly
    font_configs = [
        {"name": "MalgunGothic", "path": "C:/Windows/Fonts/malgun.ttf"},
        {"name": "MalgunGothic-Bold", "path": "C:/Windows/Fonts/malgunbd.ttf"},
        {"name": "Batang", "path": "C:/Windows/Fonts/batang.ttc"}
    ]
    
    primary_font = "Helvetica"
    has_bold = False
    
    from reportlab.lib.fonts import addMapping
    
    for config in font_configs:
        if os.path.exists(config["path"]):
            try:
                pdfmetrics.registerFont(TTFont(config["name"], config["path"]))
                if config["name"] == "MalgunGothic":
                    primary_font = config["name"]
                if config["name"] == "MalgunGothic-Bold":
                    has_bold = True
            except:
                pass
    
    # Map Bold weight if available
    if primary_font == "MalgunGothic" and has_bold:
        addMapping('MalgunGothic', 0, 0, 'MalgunGothic') # normal
        addMapping('MalgunGothic', 1, 0, 'MalgunGothic-Bold') # bold
    
    directory = current_app.config['UPLOAD_DIR']
    file_path = os.path.join(directory, asset.file_svg_path)
    
    if not os.path.exists(file_path):
        return "File not found", 404

    try:
        # 2. Preprocess SVG for svglib/ReportLab compatibility
        with open(file_path, 'r', encoding='utf-8') as f:
            svg_text = f.read()

        # Remove <style> tags and embedded fonts (crucial for svglib)
        svg_text = re.sub(r'<style>.*?</style>', '', svg_text, flags=re.DOTALL)
        
        # Map all font-family to our registered primary font (MalgunGothic)
        # This catches 'cursive', 'serif', 'sans-serif', 'Noto Serif KR', etc.
        svg_text = re.sub(r'font-family=["\'](.*?)["\']', f'font-family="{primary_font}"', svg_text)
        
        # Stripping dominant-baseline as it can sometimes cause text to disappear in old libraries
        svg_text = svg_text.replace('dominant-baseline="middle"', '')

        # 3. Convert to PNG
        drawing = svg2rlg(io.BytesIO(svg_text.encode('utf-8')))
        output = io.BytesIO()
        renderPM.drawToFile(drawing, output, fmt="PNG")
        output.seek(0)
        
        filename = os.path.basename(file_path).replace('.svg', '.png')
        return send_file(output, mimetype='image/png', as_attachment=True, download_name=filename)
    except Exception as e:
        current_app.logger.error(f"PNG conversion failed: {e}")
        return send_from_directory(directory, asset.file_svg_path, as_attachment=True)

@bp.route('/delete/<int:asset_id>', methods=['DELETE'])
@login_required
def delete(asset_id):
    asset = StampAsset.query.get_or_404(asset_id)
    if asset.user_id != current_user.id:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    # Optional: Delete physical file
    # file_path = os.path.join(current_app.config['UPLOAD_DIR'], asset.file_svg_path)
    # if os.path.exists(file_path):
    #     os.remove(file_path)
    
    db.session.delete(asset)
    db.session.commit()
    return jsonify({'status': 'success'})
