from ate_projectdatabase.Types import Types
from ate_projectdatabase.FileOperator import DBObject, FileOperator


class Die:

    @staticmethod
    def get(session: FileOperator, name: str) -> DBObject:
        return session.query(Types.Die()).filter(lambda Die: Die.name == name).one()

    @staticmethod
    def get_all(session: FileOperator) -> list:
        return session.query(Types.Die()).all()

    @staticmethod
    def add(session: FileOperator, name, hardware, maskset, quality, grade, grade_reference, type, customer, is_enabled):
        die = {"name": name, "hardware": hardware, "maskset": maskset, "quality": quality, "grade": grade,
               "grade_reference": grade_reference, "type": type, "customer": customer, "is_enabled": is_enabled}
        session.query(Types.Die()).add(die)
        session.commit()

    @staticmethod
    def update(session: FileOperator, name: str, hardware: str, maskset: str, quality: str, grade: str, grade_reference: str,
               type: str, customer: str):
        die = Die.get(session, name)
        die.hardware = hardware
        die.maskset = maskset
        die.quality = quality
        die.grade = grade
        die.grade_reference = grade_reference
        die.type = type
        die.customer = customer
        session.commit()

    @staticmethod
    def update_state(session: FileOperator, name: str, is_enabled: bool):
        die = Die.get(session, name)
        die.is_enabled = is_enabled
        session.commit()

    @staticmethod
    def remove(session: FileOperator, name: str):
        session.query(Types.Die())\
               .filter(lambda Die: Die.name == name)\
               .delete()
        session.commit()

    @staticmethod
    def get_hardware(session: FileOperator, name: str) -> list:
        return session.query(Types.Die())\
                      .filter(lambda Die: Die.hardware == name and Die.is_enabled)\
                      .all()

    @staticmethod
    def get_die(session: FileOperator, name: str) -> DBObject:
        return session.query(Types.Die())\
                      .filter(lambda Die: Die.name == name)\
                      .one()

    @staticmethod
    def get_all_for_hardware(session: FileOperator, hardware: str) -> list:
        return session.query(Types.Die())\
                      .filter(lambda Die: Die.hardware == hardware)\
                      .all()

    @staticmethod
    def get_all_for_maskset(session: FileOperator, maskset: str) -> list:
        return session.query(Types.Die())\
                      .filter(lambda Die: Die.maskset == maskset)\
                      .all()
