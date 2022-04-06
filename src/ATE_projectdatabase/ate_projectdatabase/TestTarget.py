from ate_projectdatabase.Types import Types
from ate_projectdatabase.FileOperator import DBObject, FileOperator


class TestTarget:

    @staticmethod
    def add(session: FileOperator, name: str, prog_name: str, hardware: str, base: str, test: str, is_default: bool, is_enabled: bool):
        target = {"name": name, "prog_name": prog_name, "hardware": hardware, "base": base, "test": test,
                  "is_default": is_default, "is_enabled": is_enabled, "is_changed": False, "is_changed": False}
        session.query(Types.Testtarget()).add(target)
        session.commit()

    @staticmethod
    def get(session: FileOperator, name: str, hardware: str, base: str, test: str) -> DBObject:
        return session.query(Types.Testtarget())\
                      .filter(lambda TestTarget: (TestTarget.name == name and TestTarget.hardware == hardware and TestTarget.base == base and TestTarget.test == test))\
                      .one()

    @staticmethod
    def get_all(session: FileOperator):
        return session.query(Types.Testtarget())\
                      .all()

    @staticmethod
    def get_tests(session: FileOperator, hardware: str, base: str, test_target: str) -> list:
        return session.query(Types.Testtarget())\
                      .filter(lambda TestTarget: (TestTarget.name == test_target and TestTarget.hardware == hardware and TestTarget.base == base))\
                      .all()

    @staticmethod
    def get_for_hardware_base_test(session: FileOperator, hardware: str, base: str, test: str) -> list:
        return session.query(Types.Testtarget())\
                      .filter(lambda TestTarget: (TestTarget.hardware == hardware and TestTarget.base == base and TestTarget.test == test))\
                      .all()

    @staticmethod
    def get_for_program(session: FileOperator, prog_name: str) -> list:
        return session.query(Types.Testtarget())\
                      .filter(lambda TestTarget: TestTarget.prog_name == prog_name)\
                      .all()

    @staticmethod
    def get_for_test(session: FileOperator, test_name: str, hardware: str, base: str) -> list:
        return session.query(Types.Testtarget())\
                      .filter(lambda TestTarget: TestTarget.test == test_name and TestTarget.hardware == hardware and TestTarget.base == base)\
                      .all()

    @staticmethod
    def exists(session: FileOperator, name: str, hardware: str, base: str, test: str, prog_name: str) -> bool:
        num_items = session.query(Types.Testtarget())\
                           .filter(lambda TestTarget: (TestTarget.name == name and TestTarget.prog_name == prog_name and TestTarget.hardware == hardware and TestTarget.base == base and TestTarget.test == test))\
                           .count()
        return num_items != 0

    @staticmethod
    def remove(session: FileOperator, name: str, test: str, hardware: str, base: str):
        session.query(Types.Testtarget())\
               .filter(lambda TestTarget: (TestTarget.name == name and TestTarget.test == test and TestTarget.hardware == hardware and TestTarget.base == base))\
               .delete()
        session.commit()

    @staticmethod
    def remove_for_test_program(session: FileOperator, prog_name: str):
        session.query(Types.Testtarget())\
               .filter(lambda TestTarget: TestTarget.prog_name == prog_name)\
               .delete()
        session.commit()

    @staticmethod
    def get_changed_test_targets(session: FileOperator, hardware: str, base: str, prog_name: str) -> list:
        return session.query(Types.Testtarget())\
                      .filter(lambda TestTarget: (TestTarget.is_changed and TestTarget.prog_name == prog_name and TestTarget.hardware == hardware and TestTarget.base == base))\
                      .all()

    @staticmethod
    def update_changed_state_test_targets(session: FileOperator, hardware: str, base: str, prog_name: str) -> list:
        tests = session.query(Types.Testtarget())\
                       .filter(lambda TestTarget: (TestTarget.prog_name == prog_name and TestTarget.hardware == hardware and TestTarget.base == base))\
                       .all()
        for test in tests:
            test.is_changed = False

        session.commit()

    @staticmethod
    def set_default_state(session: FileOperator, name: str, hardware: str, base: str, test: str, is_default: bool):
        test_target = TestTarget.get(session, name, hardware, base, test)
        test_target.is_default = is_default
        session.commit()

    @staticmethod
    def toggle(session: FileOperator, name: str, hardware: str, base: str, test: str, enable: bool):
        test_target = TestTarget.get(session, name, hardware, base, test)
        test_target.is_enabled = enable
        session.commit()

    @staticmethod
    def update_program_name(session: FileOperator, prog_name: str, new_prog_name: str):
        test_targets = TestTarget.get_for_program(session, prog_name)
        for test_target in test_targets:
            test_target.prog_name = new_prog_name
            session.commit()

    @staticmethod
    def update_test_changed_flag(session: FileOperator, name: str, hardware: str, base, test: str, is_changed: bool):
        test_target = TestTarget.get(session, name, hardware, base, test)
        test_target.is_changed = is_changed
        session.commit()
