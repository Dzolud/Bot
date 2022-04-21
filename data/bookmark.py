import sqlalchemy
from .db_session import SqlAlchemyBase


class Bookmarks(SqlAlchemyBase):
    __tablename__ = 'bookmarks'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    chat_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    request = sqlalchemy.Column(sqlalchemy.String, nullable=False)