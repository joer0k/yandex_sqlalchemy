from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.fields.simple import BooleanField
from wtforms.validators import DataRequired


class JobForm(FlaskForm):
    job_title = StringField('Название работы', validators=[DataRequired()])
    team_leader_id = StringField('Id лидера команды', validators=[DataRequired()])
    work_size = StringField('Объем работы', validators=[DataRequired()])
    collaborators = StringField('Соучастники', validators=[DataRequired()])
    hazard_category_id = StringField('Категория опасности', validators=[DataRequired()])
    is_finished = BooleanField('Работа завершена?')
    submit = SubmitField('Сохранить')
