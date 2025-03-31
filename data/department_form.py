from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired


class DepartmentForm(FlaskForm):
    dep_title = StringField('Название департамента', validators=[DataRequired()])
    chief_id = StringField('Id начальника', validators=[DataRequired()])
    members = StringField('Участники', validators=[DataRequired()])
    email = StringField('Почта', validators=[DataRequired()])
    submit = SubmitField('Сохранить')
