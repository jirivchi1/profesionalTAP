from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class LandingForm(FlaskForm):
    sector = SelectField('Sector', choices=[
        ('abogatap', 'AbogaTAP - Abogados'),
        ('segurotap', 'SeguroTAP - Seguros'),
        ('inmotap', 'InmoTAP - Inmobiliaria'),
        ('saludtap', 'SaludTAP - Salud'),
    ], validators=[DataRequired()])

    business_name = StringField('Nombre del negocio', validators=[
        DataRequired(), Length(max=150)
    ])
    contact_name = StringField('Nombre completo', validators=[
        DataRequired(), Length(max=150)
    ])
    phone = StringField('Teléfono', validators=[
        DataRequired(), Length(max=30)
    ])
    email = StringField('Correo electrónico', validators=[
        Optional(), Length(max=150)
    ])
    linkedin = StringField('LinkedIn (URL)', validators=[
        Optional(), Length(max=200)
    ])
    website = StringField('Página web', validators=[
        Optional(), Length(max=200)
    ])

    submit = SubmitField('Crear mi tarjeta')
