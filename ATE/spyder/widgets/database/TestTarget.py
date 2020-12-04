from sqlalchemy import and_
from sqlalchemy import Boolean
from sqlalchemy import CheckConstraint
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy.orm import relationship

from ATE.spyder.widgets.database.ORM import Base


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
    is_changed = Column(Boolean)

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
    def get_for_test(session, test_name):
        return session.query(TestTarget).filter(TestTarget.test == test_name).all()

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

    @staticmethod
    def update_program_name(session, prog_name, new_prog_name):
        test_targets = TestTarget.get_for_program(session, prog_name)
        for test_target in test_targets:
            test_target.prog_name = new_prog_name
            session.commit()

    @staticmethod
    def update_test_changed_flag(session, name, hardware, base, test, is_changed):
        test_target = TestTarget.get(session, name, hardware, base, test)
        test_target.is_changed = is_changed
        session.commit()

    @staticmethod
    def get_changed_test_targets(session, hardware, base, prog_name):
        return session.query(TestTarget).filter(TestTarget.is_changed, TestTarget.prog_name == prog_name, TestTarget.hardware == hardware, TestTarget.base == base).all()

    @staticmethod
    def update_changed_state_test_targets(session, hardware, base, prog_name):
        tests = session.query(TestTarget).filter(TestTarget.prog_name == prog_name, TestTarget.hardware == hardware, TestTarget.base == base).all()
        for test in tests:
            test.is_changed = False
