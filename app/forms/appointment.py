from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Optional, Email, Length


class AppointmentForm(FlaskForm):
    """Solo gestiona CSRF + campos visibles.
    Los campos ocultos (appt_date, appt_time, service_id) se leen
    directamente de request.form para evitar inputs duplicados."""
    name = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Teléfono', validators=[Optional(), Length(max=30)])
    message = TextAreaField('Mensaje', validators=[Optional(), Length(max=500)])
