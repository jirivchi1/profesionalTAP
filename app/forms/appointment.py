from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Optional, Email, Length


class AppointmentForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Teléfono', validators=[Optional(), Length(max=30)])
    appt_date = HiddenField('Fecha', validators=[DataRequired()])
    appt_time = HiddenField('Hora', validators=[DataRequired()])
    service_id = HiddenField('Servicio')
    message = TextAreaField('Mensaje', validators=[Optional(), Length(max=500)])
