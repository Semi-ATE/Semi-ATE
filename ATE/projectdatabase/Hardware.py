from ATE.projectdatabase.Types import Types
from ATE.projectdatabase.FileOperator import DBObject, FileOperator


class Hardware:

    @staticmethod
    def get(session: FileOperator, name: str) -> DBObject:
        return session.query(Types.Hardware())\
                      .filter(lambda Hardware: Hardware.name == name)\
                      .one()

    @staticmethod
    def get_all(session: FileOperator) -> list:
        return session.query(Types.Hardware()).all()

    @staticmethod
    def add(session: FileOperator, name: str, definition: dict, is_enabled: bool):
        hw = {"name": name, "definition": definition, "is_enabled": is_enabled}
        session.query(Types.Hardware()).add(hw)
        session.commit()

    @staticmethod
    def update(session: FileOperator, name: str, definition: dict):
        hw = Hardware.get(session, name)
        hw.definition = definition
        session.commit()

    @staticmethod
    def update_state(session: FileOperator, name: str, is_enabled: bool):
        hw = Hardware.get(session, name)
        hw.is_enabled = is_enabled
        session.commit()

    @staticmethod
    def remove(session: FileOperator, name: str):
        session.query(Types.Hardware())\
               .filter(lambda Hardware: Hardware.name == name)\
               .delete()
        session.commit()

    @staticmethod
    def get_definition(session: FileOperator, name: str) -> dict:
        hardware = Hardware.get(session, name)
        return hardware.definition
