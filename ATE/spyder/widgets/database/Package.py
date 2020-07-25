from sqlalchemy import Boolean
from sqlalchemy import CheckConstraint
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Text

from ATE.spyder.widgets.database.ORM import Base


class Package(Base):
    __tablename__ = 'packages'
    __table_args__ = (
        CheckConstraint('leads>=2 AND leads<=99'),
    )

    name = Column(Text, primary_key=True)
    leads = Column(Integer, nullable=False)
    is_enabled = Column(Boolean)
    is_naked_die = Column(Boolean)

    @staticmethod
    def add(session, name, leads, is_naked_die, is_enabled):
        package = Package(name=name, leads=leads, is_naked_die=is_naked_die, is_enabled=is_enabled)
        session.add(package)
        session.commit()

    @staticmethod
    def update(session, name, leads, is_naked_die, is_enabled=True):
        package = session.query(Package).filter(Package.name == name).one()
        package.leads = leads
        package.is_naked_die = is_naked_die
        package.is_enabled = is_enabled
        session.commit()

    @staticmethod
    def update_state(session, name, state):
        package = session.query(Package).filter(Package.name == name).one()
        package.is_enabled = state
        session.commit()

    @staticmethod
    def get(session, name):
        return session.query(Package).filter(Package.name == name).one_or_none()

    @staticmethod
    def get_all(session):
        return session.query(Package).all()

    @staticmethod
    def remove(session, name):
        session.query(Package).filter(Package.name == name).delete(synchronize_session='evaluate')
        session.commit()
