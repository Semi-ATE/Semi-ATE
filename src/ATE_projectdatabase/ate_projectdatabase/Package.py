from ate_projectdatabase.Types import Types
from ate_projectdatabase.FileOperator import DBObject, FileOperator


class Package:
    @staticmethod
    def add(session: FileOperator, name: str, leads: int, is_naked_die: bool, is_enabled: bool):
        package = {"name": name, "leads": leads, "is_naked_die": is_naked_die, "is_enabled": is_enabled}
        session.query(Types.Package()).add(package)
        session.commit()

    @staticmethod
    def update(session: FileOperator, name: str, leads: int, is_naked_die: bool, is_enabled=True):
        package = session.query(Types.Package())\
                         .filter(lambda package: package.name == name)\
                         .one()
        package.leads = leads
        package.is_naked_die = is_naked_die
        package.is_enabled = is_enabled
        session.commit()

    @staticmethod
    def update_state(session: FileOperator, name: str, state: bool):
        package = session.query(Types.Package())\
                         .filter(lambda package: package.name == name)\
                         .one()
        package.is_enabled = state
        session.commit()

    @staticmethod
    def get(session: FileOperator, name: str) -> DBObject:
        return session.query(Types.Package())\
                      .filter(lambda package: package.name == name)\
                      .one_or_none()

    @staticmethod
    def get_all(session: FileOperator) -> list:
        return session.query(Types.Package()).all()

    @staticmethod
    def remove(session: FileOperator, name: str):
        session.query(Types.Package())\
               .filter(lambda package: package.name == name)\
               .delete()
        session.commit()
