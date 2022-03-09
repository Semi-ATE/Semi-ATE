from ate_projectdatabase.Types import Types
from ate_projectdatabase.FileOperator import DBObject, FileOperator


class Version:
    @staticmethod
    def get(session: FileOperator) -> DBObject:
        return session.query(Types.Version())\
                      .one()
