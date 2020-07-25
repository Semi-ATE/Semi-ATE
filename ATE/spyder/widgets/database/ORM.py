# coding: utf-8
from sqlalchemy import Boolean
from sqlalchemy import CheckConstraint
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import LargeBinary
from sqlalchemy import Table
from sqlalchemy import Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.sqltypes import NullType


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
