from sqlalchemy import Column, Integer, LargeBinary, Text, and_
from ATE.org.database.ORM import Base

import pickle


class Sequence(Base):
    __tablename__ = 'sequence'

    id = Column(Integer, primary_key=True)
    owner_name = Column(Text, nullable=False)
    prog_name = Column(Text, nullable=False)
    test = Column(Text, nullable=False)
    test_order = Column(Integer)
    definition = Column(LargeBinary, nullable=False)

    def get_definition(self):
        return pickle.loads(self.definition)

    @staticmethod
    def add_sequence_information(session, owner_name, prog_name, test, order, definition):
        s = Sequence(owner_name=owner_name, prog_name=prog_name, test=test, test_order=order, definition=pickle.dumps(definition))
        session.add(s)
        session.commit()

    # TODO: owner_name not needed ?
    @staticmethod
    def get_for_program(session, prog_name):
        return session.query(Sequence).filter(Sequence.prog_name == prog_name).order_by(Sequence.test_order).all()

    @staticmethod
    def get_programs_for_test(session, test_name):
        return session.query(Sequence).filter(Sequence.test == test_name).all()

    @staticmethod
    def remove_test_from_sequence(session, test_name):
        session.query(Sequence).filter(Sequence.test == test_name).delete(synchronize_session='evaluate')
        session.commit()

    @staticmethod
    def remove_program_sequence(session, prog_name, owner_name):
        session.query(Sequence).filter(and_(Sequence.prog_name == prog_name, Sequence.owner_name == owner_name)).delete(synchronize_session='evaluate')
        session.commit()

    @staticmethod
    def remove_for_program(session, program_name):
        session.query(Sequence).filter(Sequence.prog_name == program_name).delete(synchronize_session='evaluate')
        session.commit()

    @staticmethod
    def update_progname(session, old_prog_name, owner_name, new_prog_name):
        progs = Sequence.get_for_program(session, old_prog_name)
        for p in progs:
            p.prog_name = new_prog_name
        session.commit()

    @staticmethod
    def update_program_name_for_sequence(session, new_prog_name, owner_name, ids):
        progs = session.query(Sequence).filter(and_(Sequence.owner_name == owner_name)).all()
        progs = [prog for prog in progs if prog.id in ids]
        for prog in progs:
            prog.prog_name = new_prog_name
        session.commit()

    @staticmethod
    def remove(session, program_name, owner_name, program_order):
        session.query(Sequence).filter(and_(Sequence.prog_name == program_name, Sequence.owner_name == owner_name)).delete(synchronize_session='evaluate')
        session.commit()
