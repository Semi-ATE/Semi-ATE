from ate_projectdatabase.Types import Types
from ate_projectdatabase.FileOperator import DBObject, FileOperator


class Device:

    @staticmethod
    def get(session: FileOperator, name: str) -> DBObject:
        return session.query(Types.Device())\
                      .filter(lambda device: device.name == name)\
                      .one()

    @staticmethod
    def get_all(session: FileOperator) -> list:
        return session.query(Types.Device())\
                      .all()

    @staticmethod
    def add(session: FileOperator, name: str, hardware: str, package: str, definition: dict, is_enabled: bool):
        # ToDo: implement constraints, i.e. hardware should exist
        device = {"name": name, "hardware": hardware, "package": package, "definition": definition, "is_enabled": is_enabled}
        session.query(Types.Device()).add(device)
        session.commit()

    @staticmethod
    def update(session: FileOperator, name: str, hardware: str, package: str, definition: dict):
        device = Device.get(session, name)
        device.hardware = hardware
        device.package = package
        device.definition = definition
        session.commit()

    @staticmethod
    def update_state(session: FileOperator, name: str, is_enabled: bool):
        device = Device.get(session, name)
        device.is_enabled = is_enabled
        session.commit()

    @staticmethod
    def remove(session: FileOperator, name: str):
        session.query(Types.Device())\
               .filter(lambda Device: Device.name == name)\
               .delete()
        session.commit()

    @staticmethod
    def get_definition(session: FileOperator, name: str) -> dict:
        device = Device.get(session, name)
        return device.definition

    @staticmethod
    def get_all_for_hardware(session: FileOperator, hardware: str) -> list:
        return session.query(Types.Device())\
                      .filter(lambda Device: Device.hardware == hardware)\
                      .all()
