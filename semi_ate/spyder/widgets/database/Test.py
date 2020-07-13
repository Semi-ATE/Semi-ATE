from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Integer, LargeBinary, Text, and_
from sqlalchemy.orm import relationship
from ATE.org.database.ORM import Base

import pickle


class Test(Base):
    __tablename__ = 'tests'
    __table_args__ = (
        CheckConstraint("base=='PR' OR base=='FT'"),
        CheckConstraint("type=='standard' OR type=='custom'")
    )

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    hardware = Column(ForeignKey('hardwares.name'), nullable=False)
    type = Column(Text, nullable=False)
    base = Column(Text, nullable=False)
    definition = Column(LargeBinary, nullable=False)
    is_enabled = Column(Boolean)

    hardware1 = relationship('Hardware')

    def get_definition(self):
        return pickle.loads(self.definition)

    @staticmethod
    def get(session, name, hardware, base):
        return session.query(Test).filter(and_(Test.name == name, Test.hardware == hardware, Test.base == base)).one()

    @staticmethod
    def get_all(session, hardware, base, test_type):
        if test_type != 'all':
            return session.query(Test).filter(and_(Test.base == base, Test.hardware == hardware, Test.type == test_type)).all()
        else:
            return session.query(Test).filter(and_(Test.base == base, Test.hardware == hardware)).all()

    @staticmethod
    def remove(session, name):
        session.query(Test).filter(Test.name == name).delete(synchronize_session='evaluate')
        session.commit()

    @staticmethod
    def update(session, name, hardware, base, type, definition, is_enabled):
        test = session.query(Test).filter(and_(Test.name == name, Test.hardware == hardware, Test.base == base)).one()
        test.definition = pickle.dumps(definition)
        test.is_enabled = is_enabled
        session.commit()

    @staticmethod
    def add(session, name, hardware, base, test_type, definition, is_enabled):
        test = Test(name=name, hardware=hardware, base=base, type=test_type, definition=pickle.dumps(definition), is_enabled=is_enabled)
        session.add(test)
        session.commit()

    @staticmethod
    def get_all_for_hardware(session, hardware):
        return session.query(Test).filter(Test.hardware == hardware).all()
