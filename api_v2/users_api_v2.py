import flask
from flask import make_response, jsonify
from flask_restful import Resource
from werkzeug.security import generate_password_hash

from api_v2.regparse_user import parser
from data import db_session
from data.users import User


def set_password(password):
    return generate_password_hash(password)


class UserResource(Resource):
    def get(self, id_user):
        session = db_session.create_session()
        user = session.query(User).get(id_user)
        if user:
            return jsonify({'users': ([user.to_dict(
                only=('id', 'surname', 'name', 'age', 'position', 'speciality', 'address', 'email', 'city_from')
            )])})
        return flask.abort(404)

    def delete(self, id_user):
        session = db_session.create_session()
        user = session.get(User, id_user)
        if user:
            session.delete(user)
            session.commit()
            return make_response(jsonify({
                'id': user.id,
                'surname': user.surname,
                'name': user.name,
                'email': user.email,
                'modified_date': user.modified_date.isoformat()
            }), 201)
        else:
            session.close()
            flask.abort(404)


class UserListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': ([item.to_dict(
            only=('id', 'surname', 'name', 'age', 'position', 'speciality', 'address', 'email', 'city_from')
        )
            for item in users])})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            surname=args['surname'],
            name=args['name'],
            age=args['age'],
            position=args['position'],
            speciality=args['speciality'],
            address=args['address'],
            email=args['email'],
            hashed_password=set_password(args['hashed_password']),
        )
        session.add(user)
        session.commit()
        return make_response(jsonify({
            'id': user.id,
            'surname': user.surname,
            'name': user.name,
            'email': user.email,
            'modified_date': user.modified_date.isoformat()
        }), 201)
