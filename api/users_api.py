
import flask

from data import db_session
from data.users import User

users_bp = flask.Blueprint('users_api', __name__, template_folder='templates')


@users_bp.route('/users', methods=['GET'])
def get_users():
    session = db_session.create_session()
    users = session.query(User).all()
    return flask.jsonify({'users': ([item.to_dict(
        only=('id', 'surname', 'name', 'age', 'position', 'speciality', 'address', 'email')
    )
        for item in users])})


@users_bp.route('/users/<int:id_user>', methods=['GET'])
def get_user(id_user):
    session = db_session.create_session()
    user = session.query(User).get(id_user)
    return flask.jsonify({'users': ([user.to_dict(
        only=('id', 'surname', 'name', 'age', 'position', 'speciality', 'address', 'email')
    )])})
