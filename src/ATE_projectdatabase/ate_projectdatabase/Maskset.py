from ate_projectdatabase.Types import Types
from ate_projectdatabase.FileOperator import DBObject, FileOperator


class Maskset:

    @staticmethod
    def get(session: FileOperator, name: str) -> DBObject:
        return session.query(Types.Maskset())\
                      .filter(lambda Maskset: Maskset.name == name)\
                      .one()

    @staticmethod
    def get_all(session: FileOperator) -> list:
        return session.query(Types.Maskset()).all()

    @staticmethod
    def add(session: FileOperator, name: str, customer: str, definition: dict, is_enabled: bool):
        maskset = {"name": name, "customer": customer, "definition": definition, "is_enabled": is_enabled}
        session.query(Types.Maskset()).add(maskset)
        session.commit()

    @staticmethod
    def update(session: FileOperator, name: str, customer: str, definition: dict):
        maskset = Maskset.get(session, name)
        maskset.definition = definition
        maskset.customer = customer
        session.commit()

    @staticmethod
    def update_state(session: FileOperator, name: str, is_enabled: bool):
        maskset = Maskset.get(session, name)
        maskset.is_enabled = is_enabled
        session.commit()

    @staticmethod
    def remove(session: FileOperator, name: str):
        session.query(Types.Maskset())\
               .filter(lambda Maskset: Maskset.name == name)\
               .delete()
        session.commit()

    @staticmethod
    def get_definition(session: FileOperator, name: str) -> dict:
        maskset = Maskset.get(session, name)
        return maskset.definition

    @staticmethod
    def get_customer(session: FileOperator, name: str) -> str:
        maskset = Maskset.get(session, name)
        return maskset.customer

    @staticmethod
    def get_ASIC_masksets(session: FileOperator) -> list:
        return session.query(Types.Maskset())\
                      .filter(lambda Maskset: Maskset.customer != '')\
                      .all()

    @staticmethod
    def get_ASSP_masksets(session: FileOperator) -> list:
        return session.query(Types.Maskset())\
                      .filter(lambda Maskset: Maskset.customer == '')\
                      .all()
