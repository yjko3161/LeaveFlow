from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.quote import Quote, QuoteItem
from app.services.approval_service import ApprovalService

bp = Blueprint('quote', __name__, url_prefix='/quote')

@bp.route('/')
@login_required
def index():
    quotes = Quote.query.filter_by(user_id=current_user.id).order_by(Quote.created_at.desc()).all()
    return render_template('quote/index.html', quotes=quotes)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_quote():
    if request.method == 'POST':
        title = request.form.get('title')
        client = request.form.get('client_name')
        
        # Snapshot Company Info
        from app.models.company import CompanyInfo
        comp = CompanyInfo.query.first()
        
        provider_name = comp.company_name if comp else "주식회사 FlexLite"
        provider_owner = comp.owner_name if comp else ""
        provider_reg = comp.registration_number if comp else ""
        provider_addr = comp.address if comp else ""
        provider_type = comp.business_type if comp else ""
        provider_item = comp.business_item if comp else ""
        provider_phone = comp.phone if comp else ""
        
        quote = Quote(
            user_id=current_user.id, 
            title=title, 
            client_name=client, 
            status_local='DRAFT',
            provider_company_name=provider_name,
            provider_owner_name=provider_owner,
            provider_reg_number=provider_reg,
            provider_address=provider_addr,
            provider_business_type=provider_type,
            provider_business_item=provider_item,
            provider_phone=provider_phone,
            provider_stamp_path=comp.stamp_path if comp else None
        )
        db.session.add(quote)
        db.session.flush()
        
        # Items
        descriptions = request.form.getlist('desc')
        specs = request.form.getlist('spec') # New
        units = request.form.getlist('unit') # New
        quantities = request.form.getlist('qty')
        prices = request.form.getlist('price')
        
        total = 0
        for i in range(len(descriptions)):
            d = descriptions[i]
            if d:
                qty = int(quantities[i]) if quantities[i] else 0
                price = int(prices[i]) if prices[i] else 0
                spec = specs[i] if i < len(specs) else ""
                unit = units[i] if i < len(units) else ""
                
                amt = qty * price
                item = QuoteItem(
                    quote_id=quote.id, 
                    description=d, 
                    spec=spec, 
                    unit=unit,
                    quantity=qty, 
                    unit_price=price, 
                    amount=amt
                )
                db.session.add(item)
                total += amt
        
        quote.total_amount = total
        quote.status_local = 'SUBMITTED'
        
        # Approval (Manager)
        approver = current_user.team.manager
        if not approver:
             from app.models.user import User
             approver = User.query.get(1)
             
        service = ApprovalService()
        req = service.create_request("QUOTE", quote.id, current_user.id, [approver.id])
        service.submit_request(req.id, current_user.id)
        
        db.session.commit()
        flash('견적서가 생성 및 상신되었습니다.', 'success')
        return redirect(url_for('quote.index'))
        
    return render_template('quote/form.html')

@bp.route('/<int:id>')
@login_required
def detail(id):
    quote = Quote.query.get_or_404(id)
    return render_template('quote/detail.html', quote=quote)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    quote = Quote.query.get_or_404(id)
    if quote.user_id != current_user.id and current_user.role != 'ADMIN':
        flash('권한이 없습니다.', 'error')
        return redirect(url_for('quote.index'))
        
    if request.method == 'POST':
        quote.title = request.form.get('title')
        quote.client_name = request.form.get('client_name')
        
        # Clear existing items to rewrite (Simple approach)
        QuoteItem.query.filter_by(quote_id=id).delete()
        
        descriptions = request.form.getlist('desc')
        specs = request.form.getlist('spec')
        units = request.form.getlist('unit')
        quantities = request.form.getlist('qty')
        prices = request.form.getlist('price')
        
        total = 0
        for i in range(len(descriptions)):
            d = descriptions[i]
            if d:
                qty = int(quantities[i]) if quantities[i] else 0
                price = int(prices[i]) if prices[i] else 0
                spec = specs[i] if i < len(specs) else ""
                unit = units[i] if i < len(units) else ""
                
                amt = qty * price
                item = QuoteItem(
                    quote_id=quote.id, 
                    description=d, 
                    spec=spec, 
                    unit=unit, 
                    quantity=qty, 
                    unit_price=price, 
                    amount=amt
                )
                db.session.add(item)
                total += amt
        
        # Refresh Stamp Snapshot (If exists)
        from app.models.company import CompanyInfo
        comp = CompanyInfo.query.first()
        if comp and comp.stamp_path:
            quote.provider_stamp_path = comp.stamp_path

        quote.total_amount = total
        db.session.commit()
        flash('견적서가 수정되었습니다.', 'success')
        return redirect(url_for('quote.detail', id=quote.id))
        
    return render_template('quote/form.html', quote=quote)

@bp.route('/<int:id>/copy', methods=['POST'])
@login_required
def copy(id):
    src = Quote.query.get_or_404(id)
    
    # Create new quote
    new_quote = Quote(
        user_id=current_user.id,
        title=f"{src.title} (사본)",
        client_name=src.client_name,
        status_local='DRAFT',
        provider_company_name=src.provider_company_name,
        provider_owner_name=src.provider_owner_name,
        provider_reg_number=src.provider_reg_number,
        provider_address=src.provider_address,
        provider_business_type=src.provider_business_type,
        provider_business_item=src.provider_business_item,
        provider_phone=src.provider_phone,
        provider_stamp_path=src.provider_stamp_path,
        total_amount=src.total_amount
    )
    db.session.add(new_quote)
    db.session.flush()
    
    # Copy Items
    for item in src.items:
        new_item = QuoteItem(
            quote_id=new_quote.id,
            description=item.description,
            spec=item.spec,
            unit=item.unit,
            quantity=item.quantity,
            unit_price=item.unit_price,
            amount=item.amount
        )
        db.session.add(new_item)
        
    db.session.commit()
    flash('견적서가 복사되었습니다. 내용을 수정하세요.', 'success')
    return redirect(url_for('quote.edit', id=new_quote.id))
