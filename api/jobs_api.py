import flask
from flask import jsonify, request
from werkzeug.exceptions import BadRequest, Conflict

from data import db_session
from data.hazard_category import HazardCategory
from data.jobs import Jobs
from data.users import User

jobs_bp = flask.Blueprint('jobs_api', __name__, template_folder='templates')


@jobs_bp.route('/jobs', methods=['GET'])
def get_jobs():
    session = db_session.create_session()
    jobs = session.query(Jobs).all()
    return flask.jsonify({'jobs': ([item.to_dict(only=(
        'id', 'job_title', 'work_size', 'collaborators', 'start_date', 'end_date', 'is_finished', 'team_leader_id',
        'hazard_category_id')) for item in jobs])})


@jobs_bp.route('/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    session = db_session.create_session()

    job = session.query(Jobs).get(job_id)
    if job:
        return flask.jsonify({'jobs': ([job.to_dict(only=(
            'id', 'job_title', 'work_size', 'collaborators', 'start_date', 'end_date', 'is_finished', 'team_leader_id',
            'hazard_category_id'))])})
    return flask.abort(404)


@jobs_bp.route('/jobs', methods=['POST'])
def create_job():
    data = request.get_json()
    required_fields = ['job_title', 'team_leader_id', 'work_size', 'collaborators', 'hazard_category_id', 'is_finished']
    if not all(field in data for field in required_fields):
        raise BadRequest('Заполните необходимые поля')

    session = db_session.create_session()
    if session.query(Jobs).filter(Jobs.job_title == data['job_title']).first():
        raise Conflict('Такая работа уже существует')
    if int(data['team_leader_id']) <= 0:
        raise Conflict('ID лидера должен быть больше 0')
    if int(data['work_size']) <= 0:
        raise Conflict('Объем работы должен быть больше 0')
    if not session.query(User).filter(User.id == int(data['team_leader_id'])).first():
        raise Conflict('Неверный ID лидера')
    if not session.query(HazardCategory).filter(HazardCategory.id == int(data['hazard_category_id'])).first():
        raise Conflict('Неверный ID категории опасности')
    try:
        job = Jobs(
            job_title=data['job_title'],
            work_size=data['work_size'],
            collaborators=data['collaborators'],
            is_finished=data['is_finished'],
            team_leader_id=data['team_leader_id'],
            hazard_category_id=data['hazard_category_id']
        )
        session.add(job)
        session.commit()

        return jsonify({
            'id': job.id,
            'job_title': job.job_title,
            'work_size': job.work_size,
            'collaborators': job.collaborators,
            'is_finished': job.is_finished,
            'team_leader_id': job.team_leader_id,
            'hazard_category_id': job.hazard_category_id
        }), 201
    except Exception as error:
        session.rollback()
        raise BadRequest(f'Ошибка создания: {str(error)}')
    finally:
        session.close()


@jobs_bp.route('/jobs/<int:id_job>', methods=['DELETE'])
def delete_job(id_job):
    session = db_session.create_session()
    job = session.query(Jobs).get(id_job)
    if job:
        session.delete(job)
        session.commit()
        return jsonify({'status': 'Успешно'}), 202
    else:
        session.close()
        flask.abort(404)


@jobs_bp.route('/jobs/<int:id_job>', methods=['PUT'])
def edit_job(id_job):
    data = request.get_json()
    session = db_session.create_session()
    if session.query(Jobs).filter(Jobs.job_title == data['job_title']).first():
        raise Conflict('Такая работа уже существует')
    if int(data['team_leader_id']) <= 0:
        raise Conflict('ID лидера должен быть больше 0')
    if int(data['work_size']) <= 0:
        raise Conflict('Объем работы должен быть больше 0')
    if not session.query(User).filter(User.id == int(data['team_leader_id'])).first():
        raise Conflict('Неверный ID лидера')
    if not session.query(HazardCategory).filter(HazardCategory.id == int(data['hazard_category_id'])).first():
        raise Conflict('Неверный ID категории опасности')
    try:
        job = session.query(Jobs).get(id_job)
        updatable_fields = ['job_title', 'team_leader_id', 'work_size',
                            'collaborators', 'is_finished', 'hazard_category_id']

        for field in updatable_fields:
            if field in data:
                setattr(job, field, data[field])

        session.commit()

        return jsonify({
            'id': job.id,
            'job_title': job.job_title,
            'work_size': job.work_size,
            'collaborators': job.collaborators,
            'is_finished': job.is_finished,
            'team_leader_id': job.team_leader_id,
            'hazard_category_id': job.hazard_category_id
        }), 200
    except Exception as error:
        session.rollback()
        raise BadRequest(f'Ошибка обновления: {str(error)}')
    finally:
        session.close()
