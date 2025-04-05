import flask
from flask_restful import Resource

from data import db_session
from data.jobs import Jobs


class JobResource(Resource):
    def get(self, id_job):
        session = db_session.create_session()

        job = session.query(Jobs).get(id_job)
        if job:
            return flask.jsonify({'jobs': ([job.to_dict(only=(
                'id', 'job_title', 'work_size', 'collaborators', 'start_date', 'end_date', 'is_finished',
                'team_leader_id',
                'hazard_category_id'))])})
        return flask.abort(404)

    def post(self):
        ...

class JobListResource(Resource):
    def get(self):
        session = db_session.create_session()
        jobs = session.query(Jobs).all()
        return flask.jsonify({'jobs': ([item.to_dict(only=(
            'id', 'job_title', 'work_size', 'collaborators', 'start_date', 'end_date', 'is_finished', 'team_leader_id',
            'hazard_category_id')) for item in jobs])})


