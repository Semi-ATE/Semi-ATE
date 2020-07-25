import pickle

from sqlalchemy import and_
from sqlalchemy import asc
from sqlalchemy import CheckConstraint
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import LargeBinary
from sqlalchemy import or_
from sqlalchemy import Text
from sqlalchemy.orm import relationship

from ATE.spyder.widgets.database.Hardware import Hardware
from ATE.spyder.widgets.database.ORM import Base
from ATE.spyder.widgets.database.TestTarget import TestTarget


class Program(Base):
    __tablename__ = 'programs'
    __table_args__ = (
        CheckConstraint("base=='PR' OR base=='FT'"),
    )

    id = Column(Integer, primary_key=True)
    prog_name = Column(Text, nullable=False)
    owner_name = Column(Text, nullable=False)
    prog_order = Column(Integer)
    hardware = Column(ForeignKey('hardwares.name'), nullable=False)
    base = Column(Text, nullable=False)
    target = Column(ForeignKey('test_targets.name'), nullable=False)
    usertext = Column(Text, nullable=False)
    sequencer_type = Column(Text, nullable=False)
    temperature = Column(LargeBinary, nullable=False)

    hardware1 = relationship('Hardware')
    test_target = relationship('TestTarget')

    @staticmethod
    def add(session, name, hardware, base, target, usertext, sequencer_typ, temperature, definition, owner_name, order, test_target):
        prog = Program(prog_name=name, hardware=hardware, base=base, target=target, usertext=usertext, sequencer_type=sequencer_typ, temperature=pickle.dumps(temperature), owner_name=owner_name, prog_order=order)
        session.add(prog)
        session.commit()

    @staticmethod
    def update(session, name, hardware, base, target, usertext, sequencer_typ, temperature, owner_name, test_target):
        prog = Program.get_by_name_and_owner(session, name, owner_name)
        prog.hardware = hardware
        prog.base = base
        prog.target = target
        prog.usertext = usertext
        prog.sequencer_type = sequencer_typ
        prog.temperature = pickle.dumps(temperature)
        session.commit()

    @staticmethod
    def remove(session, program_name, owner_name):
        session.query(Program).filter(and_(Program.prog_name == program_name, Program.owner_name == owner_name)).delete(synchronize_session='evaluate')
        session.commit()

    @staticmethod
    def get(session, name):
        return session.query(Program).filter(Program.prog_name == name).one()

    @staticmethod
    def get_by_name_and_owner(session, prog_name, owner_name):
        return session.query(Program).filter(and_(Program.prog_name == prog_name, Program.owner_name == owner_name)).one()

    @staticmethod
    def get_by_order_and_owner(session, prog_order, owner_name):
        return session.query(Program).filter(and_(Program.prog_order == prog_order, Program.owner_name == owner_name)).one()

    @staticmethod
    def update_program_name(session, prog_name, new_name):
        prog = Program.get(session, prog_name)
        prog.prog_name = new_name
        session.commit()

    @staticmethod
    def _update_program_order_neighbour(session, owner_name, prev_order, order, new_name, id):
        prog = session.query(Program).filter(and_(Program.owner_name == owner_name, Program.prog_order == prev_order, Program.id != id)).one()
        prog.prog_order = order
        prog.prog_name = new_name
        session.commit()

    @staticmethod
    def _update_program_order(session, owner_name, prev_order, order, new_name):
        prog = session.query(Program).filter(and_(Program.owner_name == owner_name, Program.prog_order == prev_order)).one()
        prog.prog_name = new_name
        prog.prog_order = order
        session.commit()

    @staticmethod
    def get_programs_for_owner(session, owner_name):
        return session.query(Program).filter(Program.owner_name == owner_name).order_by(asc(Program.prog_order)).all()

    @staticmethod
    def get_program_owner_element_count(session, owner_name):
        return session.query(Program).filter(Program.owner_name == owner_name).count()

    @staticmethod
    def get_programs_for_hardware(session, hardware):
        return session.query(Program).filter(Program.hardware == hardware).order_by(asc(Program.prog_order)).all()

    @staticmethod
    def update_program_order_and_name(session, new_name, new_order, owner_name, current_order):
        prog = Program.get_by_order_and_owner(session, current_order, owner_name)
        prog.prog_name = new_name
        prog.prog_order = new_order
        session.commit()

    @staticmethod
    def get_programs_for_target(session, target_name):
        return session.query(Program).filter(and_(Program.target == target_name)).all()
