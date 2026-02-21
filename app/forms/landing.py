from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class LandingForm(FlaskForm):
    sector = SelectField('Sector', choices=[
        ('abogatap', 'AbogaTAP - Abogados'),
        ('segurotap', 'SeguroTAP - Seguros'),
        ('inmotap', 'InmoTAP - Inmobiliaria'),
        ('consultortap', 'ConsultorTAP - Consultoría'),
    ], validators=[DataRequired()])

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

    # Services (up to 3, static fields)
    service_1_title = StringField('Servicio 1', validators=[Optional(), Length(max=150)])
    service_1_description = TextAreaField('Descripción', validators=[Optional()])

    service_2_title = StringField('Servicio 2', validators=[Optional(), Length(max=150)])
    service_2_description = TextAreaField('Descripción', validators=[Optional()])

    service_3_title = StringField('Servicio 3', validators=[Optional(), Length(max=150)])
    service_3_description = TextAreaField('Descripción', validators=[Optional()])

    submit = SubmitField('Crear mi perfil y QR')


class ContactForm(FlaskForm):
    service_id = SelectField('Servicio de interés', coerce=int, validators=[Optional()])
    name = StringField('Nombre', validators=[DataRequired(), Length(max=150)])
    email = StringField('Correo electrónico', validators=[Optional(), Length(max=150)])
    phone = StringField('Teléfono', validators=[Optional(), Length(max=30)])
    message = TextAreaField('Mensaje (opcional)', validators=[Optional()])
    submit = SubmitField('Enviar mis datos')
