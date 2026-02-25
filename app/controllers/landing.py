import json
from datetime import date, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from flask_login import login_required, current_user
from app.extensions import db
from app.forms.landing import LandingForm, ContactForm
from app.forms.appointment import AppointmentForm
from app.models.landing import LandingRequest
from app.models.landing_service import LandingService
from app.models.contact import Contact
from app.models.appointment import Appointment
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


def _build_agenda_json(req):
    """Build JSON with availability for the calendar. Returns None if no agenda configured."""
    if not req.availability:
        return None

    av0 = req.availability[0]
    weekdays = [av.day_of_week for av in req.availability]

    today = date.today()
    future = today + timedelta(days=90)
    booked = {}
    for appt in req.appointments:
        if today <= appt.date <= future:
            key = appt.date.isoformat()
            if key not in booked:
                booked[key] = []
            booked[key].append(appt.time)

    return json.dumps({
        'weekdays': weekdays,
        'start': av0.start_time,
        'end': av0.end_time,
        'slot_minutes': av0.slot_minutes,
        'booked': booked,
    })


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
    appt_form = AppointmentForm()
    agenda_json = _build_agenda_json(req)
    return render_template('landing/public_placeholder.html',
                           req=req, theme=theme, form=form,
                           appt_form=appt_form, agenda_json=agenda_json)


@landing.route('/p/<slug>/contactar', methods=['POST'])
def contact(slug):
    """Receive contact data left by someone who scanned the QR."""
    req = LandingRequest.query.filter_by(public_slug=slug).first_or_404()
    form = ContactForm()
    form.service_id.choices = _service_choices(req)
    if form.validate_on_submit():
        selected_service_id = form.service_id.data if form.service_id.data else None
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


@landing.route('/p/<slug>/cita', methods=['POST'])
def book_appointment(slug):
    """Book an appointment on a public profile."""
    req = LandingRequest.query.filter_by(public_slug=slug).first_or_404()
    appt_form = AppointmentForm()

    # Read raw form data directly — more reliable for JS-populated hidden fields
    from flask import current_app
    current_app.logger.info('CITA POST form keys: %s', list(request.form.keys()))
    current_app.logger.info('CITA POST appt_date=%r appt_time=%r name=%r',
                            request.form.get('appt_date'),
                            request.form.get('appt_time'),
                            request.form.get('name'))

    name = request.form.get('name', '').strip()
    appt_date_str = request.form.get('appt_date', '').strip()
    appt_time = request.form.get('appt_time', '').strip()

    # Still validate CSRF via appt_form
    if not appt_form.validate_on_submit() and not name:
        flash('Por favor, escribe tu nombre.', 'danger')
        return redirect(url_for('landing.public_view', slug=slug) + '#pide-cita')

    if not name:
        flash('Por favor, escribe tu nombre.', 'danger')
        return redirect(url_for('landing.public_view', slug=slug) + '#pide-cita')

    if not appt_date_str or not appt_time:
        flash('Por favor, selecciona una fecha y hora en el calendario.', 'danger')
        return redirect(url_for('landing.public_view', slug=slug) + '#pide-cita')

    try:
        appt_date = date.fromisoformat(appt_date_str)
    except (ValueError, TypeError):
        flash('Fecha no válida. Selecciona un día en el calendario.', 'danger')
        return redirect(url_for('landing.public_view', slug=slug) + '#pide-cita')

    if appt_date < date.today():
        flash('No puedes reservar una cita en el pasado.', 'danger')
        return redirect(url_for('landing.public_view', slug=slug) + '#pide-cita')

    # Prevent double-booking the same slot
    existing = Appointment.query.filter_by(
        landing_request_id=req.id,
        date=appt_date,
        time=appt_time,
    ).first()
    if existing:
        flash('Ese horario ya no está disponible. Por favor elige otro.', 'danger')
        return redirect(url_for('landing.public_view', slug=slug) + '#pide-cita')

    try:
        service_id = int(request.form.get('service_id', 0)) or None
    except ValueError:
        service_id = None

    appt = Appointment(
        landing_request_id=req.id,
        service_id=service_id,
        name=name,
        email=request.form.get('email', '').strip() or None,
        phone=request.form.get('phone', '').strip() or None,
        date=appt_date,
        time=appt_time,
        message=request.form.get('message', '').strip() or None,
    )
    db.session.add(appt)
    db.session.commit()
    flash('¡Cita reservada! Te confirmaremos lo antes posible.', 'success')
    return redirect(url_for('landing.public_view', slug=slug))
