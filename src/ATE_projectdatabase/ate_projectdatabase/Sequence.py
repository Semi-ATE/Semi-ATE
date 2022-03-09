from ate_projectdatabase.Types import Types
from ate_projectdatabase.FileOperator import FileOperator


class Sequence:

    @staticmethod
    def add_sequence_information(session: FileOperator, owner_name: str, prog_name: str, test: str, order: int, definition: dict):
        s = {"owner_name": owner_name, "prog_name": prog_name, "test": test, "test_order": order, "definition": definition}
        session.query_with_subtype(Types.Sequence(), prog_name).add(s)
        session.commit()

    @staticmethod
    def get_for_program(session: FileOperator, prog_name: str) -> list:
        return session.query_with_subtype(Types.Sequence(), prog_name)\
                      .filter(lambda Sequence: Sequence.prog_name == prog_name)\
                      .sort(lambda Sequence: Sequence.test_order)\
                      .all()

    @staticmethod
    def get_programs_for_test(session: FileOperator, test_name: str) -> list:
        return session.query(Types.Sequence())\
                      .filter(lambda Sequence: Sequence.test == test_name)\
                      .all()

    @staticmethod
    def remove_test_from_sequence(session: FileOperator, test_name: str):
        session.query(Types.Sequence())\
               .filter(lambda Sequence: Sequence.test == test_name)\
               .delete()
        session.commit()

    @staticmethod
    def remove_program_sequence(session: FileOperator, prog_name: str, owner_name: str):
        session.query(Types.Sequence())\
               .filter(lambda Sequence: (Sequence.prog_name == prog_name and Sequence.owner_name == owner_name))\
               .delete()
        session.commit()

    @staticmethod
    def remove_for_program(session: FileOperator, program_name: str):
        session.query_with_subtype(Types.Sequence(), program_name)\
               .filter(lambda Sequence: Sequence.prog_name == program_name)\
               .delete()
        session.commit()

    @staticmethod
    def update_progname(session: FileOperator, old_prog_name: str, new_prog_name: str):
        progs = Sequence.get_for_program(session, old_prog_name)
        for p in progs:
            p.prog_name = new_prog_name
        session.commit()

        # Hacky: Since this used to be done by means of sqlite which would
        # just delete everything it finds, we eat the exceptions here...
        try:
            session.rename(Types.Sequence(), old_prog_name, f"{new_prog_name}_tmp")
        except:
            pass
        try:
            session.rename(Types.Sequence(), new_prog_name, f"{old_prog_name}_tmp")
        except:
            pass
        try:
            session.rename(Types.Sequence(), f"{new_prog_name}_tmp", new_prog_name)
        except:
            pass
        try:
            session.rename(Types.Sequence(), f"{old_prog_name}_tmp", old_prog_name)
        except:
            pass

    @staticmethod
    def switch_sequences(session: FileOperator, prog_name: str, new_prog_name: str):
        Sequence.update_progname(session, prog_name, new_prog_name)

    @staticmethod
    def remove(session: FileOperator, program_name: str, owner_name: str, program_order: str):
        session.query_with_subtype(Types.Sequence(), program_name)\
               .filter(lambda Sequence: (Sequence.prog_name == program_name and Sequence.owner_name == owner_name))\
               .delete()
        session.commit()
