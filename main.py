from datetime import datetime
from os import abort

from flask import Flask, render_template, redirect, request, abort
from data import db_session
from data.users import User
from data.jobs import Jobs
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data.login_form import LoginForm
from data.register_form import RegisterForm
from data.job_form import JobForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


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
    if form.validate_on_submit():
        session = db_session.create_session()
        if session.query(Jobs).filter(Jobs.job == form.job_title.data).first():
            return render_template('job_form.html', form=form, message='Такая работа уже занесена в список')
        if int(form.team_leader_id.data) <= 0:
            return render_template('job_form.html', form=form, message='ID лидера должен быть больше 0')
        if int(form.work_size.data) <= 0:
            return render_template('job_form.html', form=form, message='Объем работы должен быть больше 0')
        if not session.query(User).filter(User.id == form.team_leader_id.data).first():
            return render_template('job_form.html', form=form, message='Неверный ID лидера')

        job = Jobs(
            job=form.job_title.data,
            work_size=form.work_size.data,
            collaborators=form.collaborators.data,
            is_finished=form.is_finished.data,
            team_leader=form.team_leader_id.data
        )
        session.add(job)
        session.commit()
        return redirect('/')
    return render_template('job_form.html', form=form, title='Добавление работы')


@app.route('/edit_job/<int:id_job>', methods=['GET', 'POST'])
@login_required
def edit_job(id_job):
    form = JobForm()
    session = db_session.create_session()
    job = session.query(Jobs).get(id_job)
    if not job:
        abort(404)
    if current_user.id != '1':
        if current_user.id != job.team_leader:
            print(current_user.id, job.team_leader, job)
            abort(401)
    if request.method == 'GET':
        form.job_title.data = job.job
        form.team_leader_id.data = job.team_leader
        form.work_size.data = job.work_size
        form.collaborators.data = job.collaborators
        form.is_finished.data = job.is_finished
    if form.validate_on_submit():
        if session.query(Jobs).filter(Jobs.job == form.job_title.data).first() and form.job_title.data != job.job:
            return render_template('job_form.html', form=form, message='Такая работа уже занесена в список')
        if int(form.team_leader_id.data) <= 0:
            return render_template('job_form.html', form=form, message='ID лидера должен быть больше 0')
        if int(form.work_size.data) <= 0:
            return render_template('job_form.html', form=form, message='Объем работы должен быть больше 0')
        if not session.query(User).filter(User.id == form.team_leader_id.data).first():
            return render_template('job_form.html', form=form, message='Неверный ID лидера')
        job.job = form.job_title.data
        job.team_leader_id = form.team_leader_id.data
        job.work_size = form.work_size.data
        job.collaborators = form.collaborators.data
        job.is_finished = form.is_finished.data
        session.commit()
        return redirect('/')

    return render_template('job_form.html', form=form, title='Изменение работы')


@app.route('/delete/<int:id_job>')
@login_required
def delete_job(id_job):
    session = db_session.create_session()
    job = session.query(Jobs).get(id_job)
    if not job:
        abort(404)
    if current_user.id != '1':
        if current_user.id != job.team_leader:
            abort(401)
    if job:
        session.delete(job)
        session.commit()
    return redirect('/')


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
    data_jobs = []
    data_leaders = {}
    session = db_session.create_session()
    for job in session.query(Jobs).all():
        data_jobs.append([job.job, job.team_leader, job.work_size, job.collaborators, job.is_finished])
        data_leaders[job.team_leader] = f'{job.user.surname} {job.user.name}'
    return render_template('works_log.html', data=data_jobs, data_leaders=data_leaders)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


if __name__ == '__main__':
    db_session.global_init('db/mars.db')
    app.run(port=8080, host='127.0.0.1', debug=True)
