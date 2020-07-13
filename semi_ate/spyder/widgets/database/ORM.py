# coding: utf-8
from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Integer, LargeBinary, Table, Text, create_engine
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session


Base = declarative_base()


class ORM:
    metadata = Base.metadata

    def __init__(self, db_file):
        self._db_engine = create_engine(f"sqlite:///{db_file}")
        self._session = sessionmaker(bind=self._db_engine)
        self._scoped_session = scoped_session(self._session)

    def init_database(self):
        self.metadata.create_all(self._db_engine)

    @property
    def session(self):
        return self._scoped_session

    def get_table(self, type, name):
        return Table(type, self.metadata, autoload=True, autoload_with=self._db_engine).columns
