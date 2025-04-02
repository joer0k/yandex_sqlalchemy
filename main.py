from os import abort

import requests
from flask import Flask, render_template, redirect, request, abort, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.exceptions import HTTPException

from api.jobs_api import jobs_bp
from api.users_api import users_bp
from data import db_session
from data.department_form import DepartmentForm
from data.departments import Department
from data.job_form import JobForm
from data.login_form import LoginForm
from data.register_form import RegisterForm
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.register_blueprint(jobs_bp, url_prefix='/api')
app.register_blueprint(users_bp, url_prefix='/api')
login_manager = LoginManager()
login_manager.init_app(app)

API_SERVER = 'http://127.0.0.1:8080/api'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_repeat.data:
            return render_template('register.html', form=form, message='Пароли не совпадают')
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', form=form, message='Пользователь с такой почтой уже существует')
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            age=form.age.data,
            position=form.position.data,
            speciality=form.speciality.data,
            address=form.address.data,
            email=form.email.data

        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', form=form)


@app.route('/addjob', methods=['GET', 'POST'])
@login_required
def add_job():
    form = JobForm()
    if request.method == 'POST' and form.validate_on_submit():
        job_data = {
            'job_title': form.job_title.data,
            'work_size': form.work_size.data,
            'collaborators': form.collaborators.data,
            'is_finished': form.is_finished.data,
            'team_leader_id': form.team_leader_id.data,
            'hazard_category_id': form.hazard_category_id.data
        }
        response = requests.post(f'{API_SERVER}/jobs', json=job_data)
        if response.status_code == 201:
            return redirect('/')
        error_data = response.json()
        return render_template('job_form.html', form=form, message=error_data.get('error'))
    return render_template('job_form.html', form=form, title='Добавление работы')


@app.route('/edit_job/<int:id_job>', methods=['GET', 'POST'])
@login_required
def edit_job(id_job):
    form = JobForm()
    if request.method == 'GET':
        response = requests.get(f'{API_SERVER}/jobs/{id_job}')
        if response.status_code != 200:
            return render_template('job_form.html', form=form, title='Изменение работы',
                                   message='Пользователь не найден')
        job_data = response.json()
        form = JobForm(data=job_data['jobs'][0])
    if request.method == 'POST' and form.validate_on_submit():
        job_data = {
            'job_title': form.job_title.data,
            'work_size': form.work_size.data,
            'collaborators': form.collaborators.data,
            'is_finished': form.is_finished.data,
            'team_leader_id': form.team_leader_id.data,
            'hazard_category_id': form.hazard_category_id.data
        }
        response = requests.put(f'{API_SERVER}/jobs/{id_job}', json=job_data)
        if response.ok:
            return redirect('/')

        error_data = response.json()
        return render_template('job_form.html', form=form, message=error_data.get('error', 'Ошибка обновления'))
    return render_template('job_form.html', form=form, title='Изменение работы')


@app.route('/delete_job/<int:id_job>')
@login_required
def delete_job(id_job):
    response = requests.delete(f'{API_SERVER}/jobs/{id_job}')
    if response:
        return redirect('/')
    abort(404)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/')
def index():
    jobs = requests.get(f'{API_SERVER}/jobs').json()
    users = requests.get(f'{API_SERVER}/users').json()
    return render_template('works_log.html', data=jobs, data_leaders=users)


@app.route('/departments')
def departments():
    data_deps = []
    data_chiefs = {}
    session = db_session.create_session()
    for dep in session.query(Department).all():
        data_deps.append([dep.id, dep.title, dep.chief, dep.members, dep.email])
        data_chiefs[dep.chief] = f'{dep.user.surname} {dep.user.name}'
    return render_template('departments_log.html', data=data_deps, data_leaders=data_chiefs)


@app.route('/add_dep', methods=['GET', 'POST'])
@login_required
def add_dep():
    form = DepartmentForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        if session.query(Department).filter(Department.title == form.dep_title.data).first():
            return render_template('dep_form.html', form=form, message='Такой департамент уже существует')
        if int(form.chief_id.data) <= 0:
            return render_template('dep_form.html', form=form, message='ID начальника должен быть больше 0')
        if not session.query(User).filter(User.id == form.chief_id.data).first():
            return render_template('dep_form.html', form=form, message='Неверный ID начальника')

        dep = Department(
            title=form.dep_title.data,
            chief=form.chief_id.data,
            members=form.members.data,
            email=form.email.data
        )
        session.add(dep)
        session.commit()
        return redirect('/departments')
    return render_template('dep_form.html', form=form, title='Добавление департамента')


@app.route('/edit_dep/<int:id_dep>', methods=['GET', 'POST'])
@login_required
def edit_dep(id_dep):
    form = DepartmentForm()
    session = db_session.create_session()
    department = session.get(Department, id_dep)
    if not department:
        abort(404)
    if current_user.id != 1:
        if current_user.id != department.chief:
            abort(401)
    if request.method == 'GET':
        form.dep_title.data = department.title
        form.chief_id.data = department.chief
        form.members.data = department.members
        form.email.data = department.email
    if form.validate_on_submit():
        if session.query(Department).filter(Department.title == form.dep_title.data).first():
            return render_template('dep_form.html', form=form, message='Такой департамент уже существует')
        if int(form.chief_id.data) <= 0:
            return render_template('dep_form.html', form=form, message='ID начальника должен быть больше 0')
        if not session.query(User).filter(User.id == form.chief_id.data).first():
            return render_template('dep_form.html', form=form, message='Неверный ID начальника')
        department.title = form.dep_title.data
        department.chief = form.chief_id.data
        department.members = form.members.data
        department.email = form.email.data
        session.commit()
        return redirect('/departments')

    return render_template('dep_form.html', form=form, title='Изменение департамента')


@app.route('/delete_dep/<int:id_dep>')
@login_required
def delete_dep(id_dep):
    session = db_session.create_session()
    dep = session.get(Department, id_dep)
    if not dep:
        abort(404)
    if current_user.id != 1:
        if current_user.id != dep.chief:
            abort(401)
    if dep:
        session.delete(dep)
        session.commit()
    return redirect('/departments')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.errorhandler(HTTPException)
def handle_http_exception(error):
    response = jsonify({
        'error': error.description,
        'status_code': error.code,
    })
    response.status_code = error.code
    return response


@app.errorhandler(Exception)
def handle_generic_exception(error):
    response = jsonify({
        'error': 'Internal server Error',
        'message': str(error)
    })
    response.status_code = 500
    return response


if __name__ == '__main__':
    db_session.global_init('db/mars.db')
    app.run(port=8080, host='127.0.0.1', debug=True)
