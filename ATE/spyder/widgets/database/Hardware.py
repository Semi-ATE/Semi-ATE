import pickle

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import LargeBinary
from sqlalchemy import Text

from ATE.spyder.widgets.database.Die import Die
from ATE.spyder.widgets.database.ORM import Base


class Hardware(Base):
    __tablename__ = 'hardwares'

    name = Column(Text, primary_key=True)
    definition = Column(LargeBinary, nullable=False)
    is_enabled = Column(Boolean)

    @staticmethod
    def get(session, name):
        return session.query(Hardware).filter(Hardware.name == name).one()

    @staticmethod
    def get_all(session):
        return session.query(Hardware).all()

    @staticmethod
    def add(session, name, definition, is_enabled):
        blob = pickle.dumps(definition, 4)
        hw = Hardware(name=name, definition=blob, is_enabled=is_enabled)
        session.add(hw)
        session.commit()

    @staticmethod
    def update(session, name, definition):
        blob = pickle.dumps(definition, 4)
        hw = Hardware.get(session, name)
        hw.definition = blob
        session.commit()

    @staticmethod
    def update_state(session, name, is_enabled):
        hw = Hardware.get(session, name)
        hw.is_enabled = is_enabled
        session.commit()

    @staticmethod
    def remove(session, name):
        session.query(Hardware).filter(Hardware.name == name).delete(synchronize_session='evaluate')
        session.commit()

    @staticmethod
    def get_definition(session, name):
        hardware = Hardware.get(session, name)
        return pickle.loads(hardware.definition)
