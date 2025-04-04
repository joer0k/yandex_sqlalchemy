import flask
from flask import request, jsonify
from werkzeug.exceptions import BadRequest, Conflict, NotFound

from data import db_session
from data.users import User

users_bp = flask.Blueprint('users_api', __name__, template_folder='templates')


@users_bp.route('/users', methods=['GET'])
def get_users():
    session = db_session.create_session()
    users = session.query(User).all()
    return flask.jsonify({'users': ([item.to_dict(
        only=('id', 'surname', 'name', 'age', 'position', 'speciality', 'address', 'email', 'city_from')
    )
        for item in users])})


@users_bp.route('/users/<int:id_user>', methods=['GET'])
def get_user(id_user):
    session = db_session.create_session()
    user = session.query(User).get(id_user)
    if user:
        return flask.jsonify({'users': ([user.to_dict(
            only=('id', 'surname', 'name', 'age', 'position', 'speciality', 'address', 'email', 'city_from')
        )])})
    return flask.abort(404)


@users_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    required_fields = ['surname', 'name', 'age', 'position',
                       'speciality', 'address', 'email',
                       'password', 'repeat_password']
    if not all(field in data for field in required_fields):
        raise BadRequest('Заполните необходимые поля')
    session = db_session.create_session()
    if data['password'] != data['repeat_password']:
        raise Conflict('Пароли не совпадают')
    if session.query(User).filter_by(email=data['email']).first():
        raise Conflict("Пользователь с указанным email уже существует!")

    try:
        user = User(
            surname=data['surname'],
            name=data['name'],
            age=data['age'],
            position=data['position'],
            speciality=data['speciality'],
            address=data['address'],
            email=data['email']
        )
        user.set_password(data['password'])
        session.add(user)
        session.commit()
        return jsonify({'id': user.id,
                        'surname': user.surname,
                        'name': user.name,
                        'email': user.email,
                        'modified_date': user.modified_date.isoformat()}), 201
    except Exception as error:
        session.rollback()
        raise BadRequest(f'Ошибка создания: {error}')
    finally:
        session.close()


@users_bp.route('/users/<int:id_user>', methods=['PUT'])
def edit_user(id_user):
    data = request.get_json()
    updatable_fields = ['surname', 'name', 'age',
                        'position', 'speciality', 'address']
    session = db_session.create_session()
    try:
        user = session.get(User, id_user)
        if not user:
            raise NotFound('Пользователь не найден')

        for field in updatable_fields:
            if field in data:
                setattr(user, field, data[field])

        if 'password' in data or 'repeat_password' in data:
            if data['password'] != data['repeat_password']:
                raise Conflict('Пароли не совпадают')
            user.set_password(data['password'])
        session.commit()

        return jsonify({
            'id': user.id,
            'surname': user.surname,
            'name': user.name,
            'email': user.email,
            'modified_date': user.modified_date.isoformat()
        }), 200
    except Exception as error:
        session.rollback()

        raise BadRequest(f'Ошибка сохранения: {error}')
    finally:
        session.close()


@users_bp.route('/users/<int:id_user>', methods=['DELETE'])
def delete_user(id_user):
    session = db_session.create_session()
    user = session.get(User, id_user)
    if user:
        session.delete(user)
        session.commit()
        return jsonify({'status': 'Успешно'}), 202
    else:
        session.close()
        flask.abort(404)
