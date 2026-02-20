from functools import wraps
from flask import Blueprint, render_template, abort, request, url_for
from flask_login import login_required, current_user
from app.models.landing import LandingRequest
from app.models.user import User
from app.extensions import db

admin = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


@admin.route('/')
@admin_required
def index():
    """Admin dashboard with analytics."""
    total = LandingRequest.query.count()
    total_b2b = LandingRequest.query.filter_by(landing_type='b2b').count()
    total_b2c = LandingRequest.query.filter_by(landing_type='b2c').count()
    total_users = User.query.count()

    # Per-sector counts
    sectors = db.session.query(
        LandingRequest.sector,
        db.func.count(LandingRequest.id)
    ).group_by(LandingRequest.sector).all()

    # Recent requests
    recent = LandingRequest.query\
        .order_by(LandingRequest.created_at.desc())\
        .limit(10).all()

    return render_template('admin/index.html',
        total=total,
        total_b2b=total_b2b,
        total_b2c=total_b2c,
        total_users=total_users,
        sectors=sectors,
        recent=recent,
    )


@admin.route('/pedidos')
@admin_required
def orders():
    """All orders with public links for NFC programming."""
    page = request.args.get('page', 1, type=int)
    filter_type = request.args.get('tipo', '')
    filter_sector = request.args.get('sector', '')

    query = LandingRequest.query

    if filter_type in ('b2b', 'b2c'):
        query = query.filter_by(landing_type=filter_type)
    if filter_sector:
        query = query.filter_by(sector=filter_sector)

    orders = query.order_by(LandingRequest.created_at.desc())\
        .paginate(page=page, per_page=25, error_out=False)

    return render_template('admin/orders.html',
        orders=orders,
        filter_type=filter_type,
        filter_sector=filter_sector,
        base_url=request.url_root.rstrip('/'),
    )
