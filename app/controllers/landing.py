from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from flask_login import login_required, current_user
from app.extensions import db
from app.forms.landing import LandingForm, ContactForm
from app.models.landing import LandingRequest
from app.models.landing_service import LandingService
from app.models.contact import Contact
from app.services.landing_service import generate_qr, build_prompt

landing = Blueprint('landing', __name__)

# Theme config per sector
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
    'consultortap': {
        'label': 'Consultoría',
        'primary': '#4f46e5',
        'bg': '#f5f3ff',
        'icon_bg': '#ede9fe',
        'icon': '\U0001f4bc',
        'community': 'ConsultorTAP',
        'community_desc': 'Conecta con consultores y asesores, comparte metodologías y amplía tu red de clientes.',
    },
}


@landing.route('/comenzar', methods=['GET', 'POST'])
def create():
    """Public — no login required."""
    form = LandingForm()
    if form.validate_on_submit():
        req = LandingRequest(
            user_id=current_user.id if current_user.is_authenticated else None,
            landing_type='b2b',
            sector=form.sector.data,
            business_name=form.contact_name.data,
            description='',
            location='',
            contact_name=form.contact_name.data,
            phone=form.phone.data,
            email=form.email.data,
            linkedin=form.linkedin.data,
            website=form.website.data,
        )
        db.session.add(req)
        db.session.flush()  # get req.id and public_slug before commit

        # Save services that have a title
        services_data = [
            (form.service_1_title.data, form.service_1_description.data),
            (form.service_2_title.data, form.service_2_description.data),
            (form.service_3_title.data, form.service_3_description.data),
        ]
        saved_services = []
        for i, (title, desc) in enumerate(services_data):
            if title and title.strip():
                svc = LandingService(
                    request_id=req.id,
                    title=title.strip(),
                    description=desc.strip() if desc else None,
                    order=i,
                )
                db.session.add(svc)
                saved_services.append(svc)

        # Generate QR pointing to the public profile
        public_url = url_for('landing.public_view', slug=req.public_slug, _external=True)
        req.qr_code = generate_qr(public_url)

        # Build AI-ready prompt from sector template and professional data
        req.generated_prompt = build_prompt(req, saved_services)

        db.session.commit()

        session['pending_request_id'] = req.id
        return redirect(url_for('landing.result', slug=req.public_slug))

    return render_template('landing/create.html', form=form)


@landing.route('/resultado/<slug>')
def result(slug):
    """Public result page — QR + community invite."""
    req = LandingRequest.query.filter_by(public_slug=slug).first_or_404()
    theme = SECTOR_THEMES.get(req.sector, SECTOR_THEMES['abogatap'])
    return render_template('landing/result.html', req=req, theme=theme)


@landing.route('/mis-landings')
@login_required
def my_landings():
    requests = LandingRequest.query.filter_by(user_id=current_user.id)\
        .order_by(LandingRequest.created_at.desc()).all()
    return render_template('landing/list.html', requests=requests)


@landing.route('/mis-landings/<int:id>')
@login_required
def detail(id):
    req = LandingRequest.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    theme = SECTOR_THEMES.get(req.sector, SECTOR_THEMES['abogatap'])
    return render_template('landing/detail.html', req=req, theme=theme)


def _service_choices(req):
    """Return [(id, title)] choices for a request's services, with a blank first option."""
    choices = [(0, 'Sin preferencia')]
    choices += [(s.id, s.title) for s in req.services]
    return choices


@landing.route('/p/<slug>')
def public_view(slug):
    """Public profile page — visible to anyone who scans the QR."""
    req = LandingRequest.query.filter_by(public_slug=slug).first_or_404()
    theme = SECTOR_THEMES.get(req.sector, SECTOR_THEMES['abogatap'])
    form = ContactForm()
    form.service_id.choices = _service_choices(req)
    return render_template('landing/public_placeholder.html', req=req, theme=theme, form=form)


@landing.route('/p/<slug>/contactar', methods=['POST'])
def contact(slug):
    """Receive contact data left by someone who scanned the QR."""
    req = LandingRequest.query.filter_by(public_slug=slug).first_or_404()
    form = ContactForm()
    form.service_id.choices = _service_choices(req)
    if form.validate_on_submit():
        selected_service_id = form.service_id.data if form.service_id.data else None
        # 0 means "sin preferencia"
        if selected_service_id == 0:
            selected_service_id = None
        c = Contact(
            request_id=req.id,
            service_id=selected_service_id,
            name=form.name.data,
            email=form.email.data or None,
            phone=form.phone.data or None,
            message=form.message.data or None,
        )
        db.session.add(c)
        db.session.commit()
        flash('¡Gracias! Tus datos han sido enviados correctamente.', 'success')
    else:
        flash('Por favor, completa al menos tu nombre.', 'danger')
    return redirect(url_for('landing.public_view', slug=slug))
