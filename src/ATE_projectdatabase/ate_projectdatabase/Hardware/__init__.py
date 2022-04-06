from ate_projectdatabase.Utils import DB_KEYS
from ate_projectdatabase.FileOperator import DBObject, FileOperator
from ate_projectdatabase.Types import Types

from ate_projectdatabase.Hardware.ParallelismStore import ParallelismStore


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
        hw = {
            DB_KEYS.HARDWARE.NAME: name,
            DB_KEYS.HARDWARE.DEFINITION.KEY(): definition,
            DB_KEYS.HARDWARE.IS_ENABLED: is_enabled
        }
        session.query(Types.Hardware()).add(hw)
        session.commit()

    @staticmethod
    def remove(session: FileOperator, name: str):
        session.query(Types.Hardware())\
               .filter(lambda Hardware: Hardware.name == name)\
               .delete()
        session.commit()

    @staticmethod
    def update_state(session: FileOperator, name: str, is_enabled: bool):
        hw = Hardware.get(session, name)
        hw.is_enabled = is_enabled
        session.commit()

    @staticmethod
    def get_state(session: FileOperator, name: str):
        return Hardware.get(session, name).is_enabled

    @staticmethod
    def update_definition(session: FileOperator, name: str, definition: dict):
        hw = Hardware.get(session, name)
        hw.definition = definition
        session.commit()

    @staticmethod
    def get_definition(session: FileOperator, name: str) -> dict:
        hardware = Hardware.get(session, name)
        return hardware.definition

    @staticmethod
    def update_parallelism_store(session: FileOperator, hw_name: str, parallelism_store: ParallelismStore):
        hw_definition = Hardware.get_definition(session, hw_name)
        hw_definition[DB_KEYS.HARDWARE.DEFINITION.PARALLELISM.KEY()] = parallelism_store.serialize()
        session.commit()

    @staticmethod
    def get_parallelism_store(session: FileOperator, hw_name: str) -> ParallelismStore:
        hw_definition = Hardware.get_definition(session, hw_name)
        return ParallelismStore.from_database(hw_definition[DB_KEYS.HARDWARE.DEFINITION.PARALLELISM.KEY()])
