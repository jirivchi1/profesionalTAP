from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user
from app.extensions import db
from app.forms.auth import LoginForm, RegisterForm
from app.models.user import User
from app.models.landing import LandingRequest

auth = Blueprint('auth', __name__)


@auth.route('/registro', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('public.home'))

    comunidad = request.args.get('comunidad', '')
    ref = request.args.get('ref', '')

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # Link pending request from session or ref param
        pending_id = session.pop('pending_request_id', None)
        if pending_id:
            req = db.session.get(LandingRequest, pending_id)
            if req and req.user_id is None:
                req.user_id = user.id
                db.session.commit()
        elif ref:
            req = LandingRequest.query.filter_by(public_slug=ref, user_id=None).first()
            if req:
                req.user_id = user.id
                db.session.commit()

        login_user(user)
        flash('¡Bienvenido a la comunidad!', 'success')

        if comunidad:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('public.home'))

    return render_template('auth/register.html', form=form, comunidad=comunidad)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('public.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Sesión iniciada correctamente.', 'success')
            return redirect(next_page or url_for('public.home'))
        flash('Email o contraseña incorrectos.', 'danger')

    return render_template('auth/login.html', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('public.home'))
