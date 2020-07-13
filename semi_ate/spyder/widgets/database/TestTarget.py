from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Integer, Text, and_
from sqlalchemy.orm import relationship
from ATE.org.database.ORM import Base
from ATE.org.database.Test import Test


class TestTarget(Base):
    __tablename__ = 'test_targets'
    __table_args__ = (
        CheckConstraint("base=='PR' OR base=='FT'"),
    )

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    prog_name = Column(Text, nullable=False)
    hardware = Column(ForeignKey('hardwares.name'), nullable=False)
    base = Column(Text, nullable=False)
    test = Column(ForeignKey('tests.name'), nullable=False)
    is_default = Column(Boolean)
    is_enabled = Column(Boolean)

    hardware1 = relationship('Hardware')
    test1 = relationship('Test')

    @staticmethod
    def add(session, name, prog_name, hardware, base, test, is_default, is_enabled):
        target = TestTarget(name=name, prog_name=prog_name, hardware=hardware, base=base, test=test, is_default=is_default, is_enabled=is_enabled)
        session.add(target)
        session.commit()

    @staticmethod
    def get(session, name, hardware, base, test):
        return session.query(TestTarget).filter(and_(TestTarget.name == name, TestTarget.hardware == hardware, TestTarget.base == base, TestTarget.test == test)).one()

    @staticmethod
    def get_tests(session, hardware, base, test_target):
        return session.query(TestTarget).filter(and_(TestTarget.name == test_target, TestTarget.hardware == hardware, TestTarget.base == base)).all()

    @staticmethod
    def get_for_hardware_base_test(session, hardware, base, test):
        return session.query(TestTarget).filter(and_(TestTarget.hardware == hardware, TestTarget.base == base, TestTarget.test == test)).all()

    @staticmethod
    def get_for_program(session, prog_name):
        return session.query(TestTarget).filter(TestTarget.prog_name == prog_name).all()

    @staticmethod
    def exists(session, name, hardware, base, test, prog_name):
        num_items = session.query(TestTarget).filter(and_(TestTarget.name == name, TestTarget.prog_name == prog_name, TestTarget.hardware == hardware, TestTarget.base == base, TestTarget.test == test)).count()
        return num_items != 0

    @staticmethod
    def remove(session, name, test, hardware, base):
        session.query(TestTarget).filter(and_(TestTarget.name == name, TestTarget.test == test, TestTarget.hardware == hardware, TestTarget.base == base)).delete(synchronize_session='evaluate')
        session.commit()

    @staticmethod
    def remove_for_test_program(session, prog_name):
        session.query(TestTarget).filter(TestTarget.prog_name == prog_name).delete(synchronize_session='evaluate')
        session.commit()

    @staticmethod
    def set_default_state(session, name, hardware, base, test, is_default):
        test_target = TestTarget.get(session, name, hardware, base, test)
        test_target.is_default = is_default
        session.commit()

    @staticmethod
    def toggle(session, name, hardware, base, test, enable):
        test_target = TestTarget.get(session, name, hardware, base, test)
        test_target.is_enabled = enable
        session.commit()
