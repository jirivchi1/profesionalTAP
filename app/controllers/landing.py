import os
from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.extensions import db
from app.forms.landing import LandingForm
from app.models.landing import LandingRequest

landing = Blueprint('landing', __name__)

SECTORS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sectors')

# Theme config per sector for B2B cards
SECTOR_THEMES = {
    'abogatap': {
        'label': 'Abogados',
        'primary': '#1e3a5f',
        'bg': '#f0f2f5',
        'icon_bg': '#e8edf3',
        'icon': '\u2696\ufe0f',
        'community': 'AbogaTAP',
        'community_desc': 'Conecta con otros profesionales del derecho, comparte casos de éxito y accede a recursos exclusivos.',
    },
    'segurotap': {
        'label': 'Seguros',
        'primary': '#0d6e3f',
        'bg': '#f0f7f4',
        'icon_bg': '#e6f4ed',
        'icon': '\U0001f6e1\ufe0f',
        'community': 'SeguroTAP',
        'community_desc': 'Únete a la red de agentes de seguros, comparte estrategias y haz crecer tu cartera.',
    },
    'inmotap': {
        'label': 'Inmobiliaria',
        'primary': '#7c5c2e',
        'bg': '#f7f4f0',
        'icon_bg': '#f0ebe3',
        'icon': '\U0001f3e0',
        'community': 'InmoTAP',
        'community_desc': 'Conecta con agentes inmobiliarios, comparte propiedades y cierra más operaciones.',
    },
    'saludtap': {
        'label': 'Salud',
        'primary': '#0e7490',
        'bg': '#f0f9fb',
        'icon_bg': '#e0f4f8',
        'icon': '\U0001fa7a',
        'community': 'SaludTAP',
        'community_desc': 'Forma parte de la comunidad de profesionales de salud, comparte conocimiento y colabora.',
    },
}


def render_b2b_card(sector, business_name, contact_name, phone, email, linkedin, website):
    """Render B2B contact card HTML from template — no AI needed."""
    theme = SECTOR_THEMES.get(sector, SECTOR_THEMES['abogatap'])
    return render_template('landing/cards/b2b_card.html',
        theme=theme,
        sector_label=theme['label'],
        business_name=business_name,
        contact_name=contact_name,
        phone=phone or '',
        email=email or '',
        linkedin=linkedin or '',
        website=website or '',
    )


@landing.route('/comenzar', methods=['GET', 'POST'])
def create():
    """Public — no login required."""
    form = LandingForm()
    if form.validate_on_submit():
        generated_html = render_b2b_card(
            sector=form.sector.data,
            business_name=form.business_name.data,
            contact_name=form.contact_name.data,
            phone=form.phone.data,
            email=form.email.data,
            linkedin=form.linkedin.data,
            website=form.website.data,
        )

        req = LandingRequest(
            user_id=current_user.id if current_user.is_authenticated else None,
            landing_type='b2b',
            sector=form.sector.data,
            business_name=form.business_name.data,
            description='',
            location='',
            contact_name=form.contact_name.data,
            phone=form.phone.data,
            email=form.email.data,
            linkedin=form.linkedin.data,
            website=form.website.data,
            generated_html=generated_html,
        )
        db.session.add(req)
        db.session.commit()

        # Store in session so we can link after registration
        session['pending_request_id'] = req.id

        return redirect(url_for('landing.result', slug=req.public_slug))
    return render_template('landing/create.html', form=form)


@landing.route('/resultado/<slug>')
def result(slug):
    """Public result page — preview + payment + community invite."""
    req = LandingRequest.query.filter_by(public_slug=slug).first_or_404()
    theme = SECTOR_THEMES.get(req.sector, SECTOR_THEMES['abogatap'])
    return render_template('landing/result.html', req=req, theme=theme)


@landing.route('/mis-landings')
@login_required
def list():
    requests = LandingRequest.query.filter_by(user_id=current_user.id)\
        .order_by(LandingRequest.created_at.desc()).all()
    return render_template('landing/list.html', requests=requests)


@landing.route('/p/<slug>')
def public_view(slug):
    """Public NFC card page — no login required."""
    req = LandingRequest.query.filter_by(public_slug=slug).first_or_404()
    if req.generated_html:
        return req.generated_html
    return render_template('landing/public_placeholder.html', req=req)
