from flask import render_template
from flask_login import login_required, current_user
from app.main import bp
from app.models import Customer, Deal

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    customers_count = Customer.query.filter_by(user_id=current_user.id).count()
    deals_count = Deal.query.filter_by(user_id=current_user.id).count()
    recent_deals = Deal.query.filter_by(user_id=current_user.id).order_by(Deal.created_at.desc()).limit(5).all()
    return render_template('main/index.html', title='Главная',
                         customers_count=customers_count,
                         deals_count=deals_count,
                         recent_deals=recent_deals) 