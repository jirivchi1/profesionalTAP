from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class ProfessionalForm(FlaskForm):
    name = StringField('Nombre completo', validators=[
        DataRequired(), Length(max=120)
    ])
    specialty = StringField('Especialidad', validators=[
        Optional(), Length(max=120)
    ])
    phone = StringField('Teléfono', validators=[
        Optional(), Length(max=20)
    ])
    bio = TextAreaField('Biografía', validators=[
        Optional(), Length(max=1000)
    ])
    submit = SubmitField('Guardar')
