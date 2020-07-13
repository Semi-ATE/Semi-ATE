from sqlalchemy import Boolean, Column, ForeignKey, LargeBinary, Text
from sqlalchemy.orm import relationship
from ATE.org.database.ORM import Base

import pickle


class Device(Base):
    __tablename__ = 'devices'

    name = Column(Text, primary_key=True)
    hardware = Column(ForeignKey('hardwares.name'), nullable=False)
    package = Column(ForeignKey('packages.name'), nullable=False)
    definition = Column(LargeBinary, nullable=False)
    is_enabled = Column(Boolean)

    hardware1 = relationship('Hardware')
    package1 = relationship('Package')

    @staticmethod
    def get(session, name):
        return session.query(Device).filter(Device.name == name).one()

    @staticmethod
    def get_all(session):
        return session.query(Device).all()

    @staticmethod
    def add(session, name, hardware, package, definition, is_enabled):
        blob = pickle.dumps(definition, 4)
        device = Device(name=name, hardware=hardware, package=package, definition=blob, is_enabled=is_enabled)
        session.add(device)
        session.commit()

    @staticmethod
    def update(session, name, hardware, package, definition):
        blob = pickle.dumps(definition, 4)
        device = Device.get(session, name)
        device.hardware = hardware
        device.package = package
        device.definition = blob
        session.commit()

    @staticmethod
    def update_state(session, name, is_enabled):
        device = Device.get(session, name)
        device.is_enabled = is_enabled
        session.commit()

    @staticmethod
    def remove(session, name):
        session.query(Device).filter(Device.name == name).delete(synchronize_session='evaluate')
        session.commit()

    @staticmethod
    def get_definition(session, name):
        device = Device.get(session, name)
        return pickle.loads(device.definition)

    @staticmethod
    def get_all_for_hardware(session, hardware):
        return session.query(Device).filter(Device.hardware == hardware).all()

