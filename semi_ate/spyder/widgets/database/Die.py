from sqlalchemy import Boolean, Column, ForeignKey, Text
from sqlalchemy.orm import relationship
from ATE.org.database.ORM import Base


class Die(Base):
    __tablename__ = 'dies'

    name = Column(Text, primary_key=True)
    hardware = Column(ForeignKey('hardwares.name'), nullable=False)
    maskset = Column(ForeignKey('masksets.name'), nullable=False)
    grade = Column(Text, nullable=False)
    grade_reference = Column(Text, nullable=False)
    quality = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    customer = Column(Text, nullable=False)
    is_enabled = Column(Boolean)

    hardware1 = relationship('Hardware')
    maskset1 = relationship('Maskset')

    @staticmethod
    def get(session, name):
        return session.query(Die).filter(Die.name == name).one()

    @staticmethod
    def get_all(session):
        return session.query(Die).all()

    @staticmethod
    def add(session, name, hardware, maskset, quality, grade, grade_reference, type, customer, is_enabled):
        die = Die(name=name, hardware=hardware, maskset=maskset, quality=quality, grade=grade,
                  grade_reference=grade_reference, type=type, customer=customer, is_enabled=is_enabled)
        session.add(die)
        session.commit()

    @staticmethod
    def update(session, name, hardware, maskset, quality, grade, grade_reference, type, customer):
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
    def update_state(session, name, is_enabled):
        die = Die.get(session, name)
        die.is_enabled = is_enabled
        session.commit()

    @staticmethod
    def remove(session, name):
        session.query(Die).filter(Die.name == name).delete(synchronize_session='evaluate')
        session.commit()

    @staticmethod
    def get_hardware(session, name):
        return session.query(Die).filter(Die.hardware == name and Die.is_enabled).all()

    @staticmethod
    def get_die(session, name):
        return session.query(Die).filter(Die.name == name).one()

    @staticmethod
    def get_all_for_hardware(session, hardware):
        return session.query(Die).filter(Die.hardware == hardware).all()

    @staticmethod
    def get_all_for_maskset(session, maskset):
        return session.query(Die).filter(Die.maskset == maskset).all()

