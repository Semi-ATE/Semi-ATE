from ate_projectdatabase.Types import Types
from ate_projectdatabase.FileOperator import DBObject, FileOperator


class Test:

    @staticmethod
    def get(session: FileOperator, name: str, hardware: str, base: str) -> DBObject:
        return session.query(Types.Test())\
                      .filter(lambda Test: (Test.name == name and Test.hardware == hardware and Test.base == base))\
                      .one()

    @staticmethod
    def get_one_or_none(session: FileOperator, name: str, hardware: str, base: str) -> DBObject:
        return session.query(Types.Test())\
                      .filter(lambda Test: (Test.name == name and Test.hardware == hardware and Test.base == base))\
                      .one_or_none()

    @staticmethod
    def get_for_hw_base_test_typ(session: FileOperator, hardware: str, base: str, test_type: str) -> list:
        if test_type != 'all':
            return session.query(Types.Test())\
                          .filter(lambda Test: (Test.base == base and Test.hardware == hardware and Test.type == test_type))\
                          .all()
        else:
            return session.query(Types.Test())\
                          .filter(lambda Test: (Test.base == base and Test.hardware == hardware))\
                          .all()

    @staticmethod
    def get_all(session: FileOperator) -> list:
        return session.query(Types.Test())\
                      .all()

    @staticmethod
    def remove(session: FileOperator, name: str, hardware: str, base: str):
        session.query(Types.Test())\
               .filter(lambda Test: Test.name == name and Test.hardware == hardware and Test.base == base)\
               .delete()
        session.commit()

    @staticmethod
    def replace(session: FileOperator, database):
        name = database['name']
        hardware = database['hardware']
        base = database['base']
        test_type = database['type']
        session.query(Types.Test())\
               .filter(lambda Test: Test.name == name and Test.hardware == hardware and Test.base == base)\
               .delete()

        test = {"name": name, "hardware": hardware, "base": base, "type": test_type, "definition": database, "is_enabled": True}
        session.query(Types.Test()).add(test)

        session.commit()

    @staticmethod
    def update(session: FileOperator, name: str, hardware: str, base: str, type: str, definition: dict, is_enabled: bool):
        test = session.query(Types.Test())\
                      .filter(lambda Test: (Test.name == name and Test.hardware == hardware and Test.base == base))\
                      .one()
        test.definition = definition
        test.is_enabled = is_enabled
        session.commit()

    @staticmethod
    def add(session: FileOperator, name: str, hardware: str, base: str, test_type: str, definition: dict, is_enabled: bool):
        test = {"name": name, "hardware": hardware, "base": base, "type": test_type, "definition": definition, "is_enabled": is_enabled}
        session.query(Types.Test()).add(test)
        session.commit()

    @staticmethod
    def get_all_for_hardware(session: FileOperator, hardware: str) -> list:
        return session.query(Types.Test()).filter(lambda Test: Test.hardware == hardware).all()
