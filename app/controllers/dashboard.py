from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.forms.professional import ProfessionalForm
from app.forms.service import ServiceForm
from app.models.professional import Professional
from app.models.service import Service
from app.models.landing import LandingRequest
from app.models.contact import Contact

dashboard = Blueprint('dashboard', __name__)


def _generar_mensaje(req, contact, service_name):
    y_servicio = f' y te interesó el servicio "{service_name}"' if service_name else ''
    profesional = req.contact_name or req.business_name
    telefono = req.phone or '—'
    email_prof = req.email or '—'
    return (
        f"Hola {contact.name},\n\n"
        f"He visto que escaneaste mi QR{y_servicio}.\n\n"
        f"Soy {profesional} y me encantaría contarte cómo puedo ayudarte.\n\n"
        f"¿Tienes unos minutos esta semana para una llamada rápida?\n\n"
        f"Puedes contactarme en:\n"
        f"📞 {telefono}\n"
        f"✉️ {email_prof}\n\n"
        f"¡Quedo a tu disposición!\n"
        f"{profesional}"
    )


@dashboard.route('/dashboard')
@login_required
def index():
    landing_requests = LandingRequest.query.filter_by(user_id=current_user.id)\
        .order_by(LandingRequest.created_at.desc()).all()
    return render_template('dashboard/index.html', landing_requests=landing_requests)


@dashboard.route('/dashboard/mensaje/<int:contact_id>')
@login_required
def mensaje(contact_id):
    contact = db.session.get(Contact, contact_id)
    if not contact or contact.request.user_id != current_user.id:
        abort(403)
    req = contact.request
    service_name = contact.service.title if contact.service_id else None
    return jsonify({'message': _generar_mensaje(req, contact, service_name)})


# --- Professional profile ---

@dashboard.route('/perfil/crear', methods=['GET', 'POST'])
@login_required
def create_profile():
    if current_user.professional:
        return redirect(url_for('dashboard.edit_profile'))

    form = ProfessionalForm()
    if form.validate_on_submit():
        prof = Professional(
            user_id=current_user.id,
            name=form.name.data,
            specialty=form.specialty.data,
            phone=form.phone.data,
            bio=form.bio.data,
        )
        db.session.add(prof)
        db.session.commit()
        flash('Perfil profesional creado.', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('dashboard/profile_form.html', form=form, title='Crear perfil profesional')


@dashboard.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def edit_profile():
    prof = current_user.professional
    if not prof:
        return redirect(url_for('dashboard.create_profile'))

    form = ProfessionalForm(obj=prof)
    if form.validate_on_submit():
        form.populate_obj(prof)
        db.session.commit()
        flash('Perfil actualizado.', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('dashboard/profile_form.html', form=form, title='Editar perfil profesional')


# --- Services CRUD ---

@dashboard.route('/servicios/crear', methods=['GET', 'POST'])
@login_required
def create_service():
    prof = current_user.professional
    if not prof:
        flash('Primero debes crear tu perfil profesional.', 'info')
        return redirect(url_for('dashboard.create_profile'))

    form = ServiceForm()
    if form.validate_on_submit():
        service = Service(
            professional_id=prof.id,
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
        )
        db.session.add(service)
        db.session.commit()
        flash('Servicio creado.', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('dashboard/service_form.html', form=form, title='Añadir servicio')


@dashboard.route('/servicios/<int:service_id>/editar', methods=['GET', 'POST'])
@login_required
def edit_service(service_id):
    service = db.session.get(Service, service_id)
    if not service or not current_user.professional or service.professional_id != current_user.professional.id:
        abort(403)

    form = ServiceForm(obj=service)
    if form.validate_on_submit():
        form.populate_obj(service)
        db.session.commit()
        flash('Servicio actualizado.', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('dashboard/service_form.html', form=form, title='Editar servicio')


@dashboard.route('/servicios/<int:service_id>/eliminar', methods=['POST'])
@login_required
def delete_service(service_id):
    service = db.session.get(Service, service_id)
    if not service or not current_user.professional or service.professional_id != current_user.professional.id:
        abort(403)

    db.session.delete(service)
    db.session.commit()
    flash('Servicio eliminado.', 'success')
    return redirect(url_for('dashboard.index'))
