from sqlalchemy import Boolean, Column, LargeBinary, Text
from ATE.org.database.ORM import Base

import pickle


class Maskset(Base):
    __tablename__ = 'masksets'

    name = Column(Text, primary_key=True)
    customer = Column(Text, nullable=False)
    definition = Column(LargeBinary, nullable=False)
    is_enabled = Column(Boolean)

    @staticmethod
    def get(session, name):
        return session.query(Maskset).filter(Maskset.name == name).one()

    @staticmethod
    def get_all(session):
        return session.query(Maskset).all()

    @staticmethod
    def add(session, name, customer, definition, is_enabled):
        blob = pickle.dumps(definition, 4)
        maskset = Maskset(name=name, customer=customer, definition=blob, is_enabled=is_enabled)
        session.add(maskset)
        session.commit()

    @staticmethod
    def update(session, name, customer, definition):
        blob = pickle.dumps(definition, 4)
        maskset = Maskset.get(session, name)
        maskset.definition = blob
        # TODO: update customer
        # maskset.customer = customer
        session.commit()

    @staticmethod
    def update_state(session, name, is_enabled):
        maskset = Maskset.get(session, name)
        maskset.is_enabled = is_enabled
        session.commit()

    @staticmethod
    def remove(session, name):
        session.query(Maskset).filter(Maskset.name == name).delete(synchronize_session='evaluate')
        session.commit()

    @staticmethod
    def get_definition(session, name):
        maskset = Maskset.get(session, name)
        return pickle.loads(maskset.definition)

    @staticmethod
    def get_customer(session, name):
        maskset = Maskset.get(session, name)
        return maskset.customer

    @staticmethod
    def get_ASIC_masksets(session):
        return session.query(Maskset).filter(Maskset.customer != '').all()

    @staticmethod
    def get_ASSP_masksets(session):
        return session.query(Maskset).filter(Maskset.customer == '').all()
