from flask import Blueprint, render_template, abort
from app.models.professional import Professional

public = Blueprint('public', __name__)


@public.route('/')
def home():
    return render_template('public/home.html')


@public.route('/about')
def about():
    return render_template('public/about.html')


@public.route('/contacto')
def contact():
    return render_template('public/contact.html')


@public.route('/profesionales')
def professionals():
    pros = Professional.query.order_by(Professional.created_at.desc()).all()
    return render_template('public/professionals.html', professionals=pros)


@public.route('/profesionales/<int:prof_id>')
def professional_detail(prof_id):
    prof = Professional.query.get_or_404(prof_id)
    return render_template('public/professional_detail.html', professional=prof)
