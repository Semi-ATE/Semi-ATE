from ate_projectdatabase.Types import Types
from ate_projectdatabase.FileOperator import DBObject, FileOperator


class Product:

    @staticmethod
    def get(session: FileOperator, name: str) -> DBObject:
        return session.query(Types.Product())\
                      .filter(lambda Product: Product.name == name)\
                      .one_or_none()

    @staticmethod
    def get_all(session: FileOperator) -> list:
        return session.query(Types.Product()).all()

    @staticmethod
    def add(session: FileOperator, name: str, device: str, hardware: str, quality: str, grade: str,
            grade_reference: str, type: str, customer: str, is_enabled=True):
        # existing_products = Product.get_all(session)
        # if name in existing_products:
        #     raise KeyError(f"product '{name}' already exists")
        product = {"name": name, "device": device, "hardware": hardware, "is_enabled": is_enabled,
                   "grade": grade, "quality": quality, "grade_reference": grade_reference, "type": type,
                   "customer": customer}
        session.query(Types.Product())
        session.add(product)
        session.commit()

    @staticmethod
    def update(session: FileOperator, name: str, device: str, hardware: str,
               quality: str, grade: str, grade_reference: str, type: str,
               customer: str, is_enabled=True):
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
    def update_state(session: FileOperator, name: str, state: bool):
        product = session.query(Types.Product())\
                         .filter(lambda Product: Product.name == name)\
                         .one()
        product.is_enabled = state
        session.commit()

    @staticmethod
    def get_for_hardware(session: FileOperator, hardware: str) -> list:
        return session.query(Types.Product())\
                      .filter(lambda Product: Product.hardware == hardware)\
                      .all()

    @staticmethod
    def get_for_device(session: FileOperator, device_name: str) -> list:
        return session.query(Types.Product())\
                      .filter(lambda Product: Product.device == device_name)\
                      .all()

    @staticmethod
    def remove(session: FileOperator, name: str):
        session.query(Types.Product())\
               .filter(lambda Product: Product.name == name)\
               .delete()
        session.commit()

    @staticmethod
    def get_all_for_hardware(session: FileOperator, hardware: str) -> list:
        return session.query(Types.Product())\
                      .filter(lambda Product: Product.hardware == hardware)\
                      .all()
