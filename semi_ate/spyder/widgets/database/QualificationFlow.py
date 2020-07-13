from sqlalchemy import Column, ForeignKey, LargeBinary, Text, and_
from sqlalchemy.orm import relationship
from ATE.org.database.ORM import Base

import pickle


class QualificationFlowDatum(Base):
    __tablename__ = 'qualification_flow_data'

    name = Column(Text, primary_key=True)
    type = Column(Text, nullable=False)
    product = Column(ForeignKey('products.name'), nullable=False)
    data = Column(LargeBinary, nullable=False)

    product1 = relationship('Product')

    def get_definition(self):
        if self.data is None:
            return {'product': self.product}

        flow_data = pickle.loads(self.data)
        if 'product' not in flow_data:
            flow_data['product'] = self.product
        if 'name' not in flow_data:
            flow_data['name'] = self.name
        if 'type' not in flow_data:
            flow_data['type'] = self.type
        return flow_data

    @staticmethod
    def get_data_for_flow(session, flow_type, product):
        return session.query(QualificationFlowDatum).filter(and_(QualificationFlowDatum.type == flow_type, QualificationFlowDatum.product == product)).all()

    @staticmethod
    def _get_by_name(session, name):
        return session.query(QualificationFlowDatum).filter(QualificationFlowDatum.name == name).one_or_none()

    @staticmethod
    def add_or_update_qualification_flow_data(session, quali_flow_data):
        item = QualificationFlowDatum._get_by_name(session, quali_flow_data["name"])
        if item is None:
            item = QualificationFlowDatum()
            session.add(item)
        item.name = quali_flow_data["name"]
        item.type = quali_flow_data["type"]
        item.product = quali_flow_data["product"]
        item.data = pickle.dumps(quali_flow_data)

        session.commit()

    @staticmethod
    def remove(session, quali_flow_data):
        session.query(QualificationFlowDatum).filter(and_(QualificationFlowDatum.name == quali_flow_data.name, QualificationFlowDatum.type == quali_flow_data.type, QualificationFlowDatum.product == quali_flow_data.product)).delete(synchronize_session='evaluate')
        session.commit()
