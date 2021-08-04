from ATE.projectdatabase.Types import Types
from ATE.projectdatabase.FileOperator import DBObject, FileOperator


class Version:
    @staticmethod
    def get(session: FileOperator) -> DBObject:
        return session.query(Types.Version())\
                      .one()
