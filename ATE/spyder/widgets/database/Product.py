from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Text
from sqlalchemy.orm import relationship

from ATE.spyder.widgets.database.ORM import Base


class Product(Base):
    __tablename__ = 'products'

    name = Column(Text, primary_key=True)
    device = Column(ForeignKey('devices.name'), nullable=False)
    hardware = Column(ForeignKey('hardwares.name'), nullable=False)
    is_enabled = Column(Boolean)
    grade = Column(Text, nullable=False)
    grade_reference = Column(Text, nullable=False)
    quality = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    customer = Column(Text, nullable=False)

    device1 = relationship('Device')
    hardware1 = relationship('Hardware')

    @staticmethod
    def get(session, name):
        return session.query(Product).filter(Product.name == name).one_or_none()

    @staticmethod
    def get_all(session):
        return session.query(Product).all()

    @staticmethod
    def add(session, name, device, hardware, quality, grade, grade_reference, type, customer, is_enabled=True):
        existing_products = Product.get_all(session)
        if name in existing_products:
            raise KeyError(f"package '{name}' already exists")
        product = Product(name=name, device=device, hardware=hardware, is_enabled=is_enabled,
                          grade=grade, quality=quality, grade_reference=grade_reference, type=type,
                          customer=customer)
        session.add(product)
        session.commit()

    @staticmethod
    def update(session, name, device, hardware, quality, grade, grade_reference, type, customer, is_enabled=True):
        prod = Product.get(session, name)
        prod.device = device
        prod.hardware = hardware
        prod.quality = quality
        prod.grade = grade
        prod.grade_reference = grade_reference
        prod.type = type
        prod.customer = customer
        prod.is_enabled = is_enabled
        session.commit()

    @staticmethod
    def update_state(session, name, state):
        product = session.query(Product).filter(Product.name == name).one()
        product.is_enabled = state
        session.commit()

    @staticmethod
    def get_for_hardware(session, hardware):
        return session.query(Product).filter(Product.hardware == hardware).all()

    @staticmethod
    def get_for_device(session, device_name):
        return session.query(Product).filter(Product.device == device_name).all()

    @staticmethod
    def remove(session, name):
        session.query(Product).filter(Product.name == name).delete(synchronize_session='evaluate')
        session.commit()

    @staticmethod
    def get_all_for_hardware(session, hardware):
        return session.query(Product).filter(Product.hardware == hardware).all()
