from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, EmailField, StringField
from wtforms.validators import DataRequired, Optional


class RegisterForm(FlaskForm):
    email = EmailField('Логин/Почта', validators=[DataRequired()])

    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    age = StringField('Возраст', validators=[DataRequired()])
    position = StringField('Позиция', validators=[DataRequired()])
    speciality = StringField('Специальность', validators=[DataRequired()])
    address = StringField('Адрес', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

    password = PasswordField('Пароль', validators=[Optional()])
    password_repeat = PasswordField('Повторите пароль', validators=[Optional()])

    def __init__(self, *args, is_editing=False, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.is_editing = is_editing

        if not self.is_editing:
            self.password.validators = [DataRequired()]
            self.password_repeat.validators = [DataRequired()]
            self.submit.label.text = 'Зарегистрироваться'
        else:
            self.submit.label.text = 'Сохранить изменения'
