import datetime

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Jobs(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'jobs'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    job_title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    work_size = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    collaborators = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    start_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    end_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    is_finished = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    team_leader_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    user = orm.relationship('User')
    hazard_category_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("hazard_category.id"),
                                           nullable=True)
    hazard_category = orm.relationship('HazardCategory')

    def __repr__(self):
        return f'<Job> {self.job}'
