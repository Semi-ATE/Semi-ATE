from ate_projectdatabase.Types import Types
from ate_projectdatabase.FileOperator import DBObject, FileOperator


class Settings:

    @staticmethod
    def _generate_settings(session: FileOperator):
        settings = {
            "quality_grade": ""
        }
        session.query(Types.Settings()).add(settings)
        session.commit()

    @staticmethod
    def get(session: FileOperator) -> DBObject:
        if session.query(Types.Settings()).one_or_none() is None:
            Settings._generate_settings(session)
        return session.query(Types.Settings()).one()

    @staticmethod
    def set_quality_grade(session: FileOperator, quality_grade: str) -> None:
        settings = Settings.get(session)
        settings.quality_grade = quality_grade
        session.commit()

    @staticmethod
    def get_quality_grade(session: FileOperator) -> str:
        setting = Settings.get(session)
        return setting.quality_grade
