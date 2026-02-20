from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange


class ServiceForm(FlaskForm):
    title = StringField('Título del servicio', validators=[
        DataRequired(), Length(max=150)
    ])
    description = TextAreaField('Descripción', validators=[
        Optional(), Length(max=2000)
    ])
    price = FloatField('Precio (€)', validators=[
        Optional(), NumberRange(min=0, message='El precio debe ser positivo')
    ])
    submit = SubmitField('Guardar')
