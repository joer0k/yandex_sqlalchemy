import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class HazardCategory(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'hazard_category'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    category = sqlalchemy.Column(sqlalchemy.String, nullable=True)