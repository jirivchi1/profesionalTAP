from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Optional, Email, Length


class AppointmentForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Teléfono', validators=[Optional(), Length(max=30)])
    # Hidden fields set by JS — validated manually in the controller
    appt_date = HiddenField('Fecha')
    appt_time = HiddenField('Hora')
    service_id = HiddenField('Servicio')
    message = TextAreaField('Mensaje', validators=[Optional(), Length(max=500)])
