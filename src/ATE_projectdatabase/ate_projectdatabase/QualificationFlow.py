from ate_projectdatabase.Types import Types
from ate_projectdatabase.FileOperator import DBObject, FileOperator


class QualificationFlowDatum:

    # To Do: Check how this is actually used.
    # def get_definition(self):
    #     if self.data is None:
    #         return {'product': self.product}

    #     flow_data = pickle.loads(self.data)
    #     if 'product' not in flow_data:
    #         flow_data['product'] = self.product
    #     if 'name' not in flow_data:
    #         flow_data['name'] = self.name
    #     if 'type' not in flow_data:
    #         flow_data['type'] = self.type
    #     return flow_data

    @staticmethod
    def get_data_for_flow(session: FileOperator, flow_type: str, product: str) -> DBObject:
        return session.query(Types.Qualification())\
                      .filter(lambda QualificationFlowDatum: (QualificationFlowDatum.type == flow_type and QualificationFlowDatum.product == product))\
                      .all()

    @staticmethod
    def _get_by_name(session: FileOperator, name: str) -> DBObject:
        return session.query(Types.Qualification())\
                      .filter(lambda QualificationFlowDatum: QualificationFlowDatum.name == name)\
                      .one_or_none()

    @staticmethod
    def add_or_update_qualification_flow_data(session: FileOperator, quali_flow_data: DBObject):
        item = QualificationFlowDatum._get_by_name(session, quali_flow_data.read_attribute("name"))
        if item is not None:
            session.filter(lambda x: x.name == item.name).delete()

        session.add(quali_flow_data.to_dict())
        session.commit()

    @staticmethod
    def remove(session: FileOperator, quali_flow_data: DBObject):
        session.query(Types.Qualification()) \
               .filter(lambda QualificationFlowDatum: (QualificationFlowDatum.name == quali_flow_data.name and QualificationFlowDatum.type == quali_flow_data.type and QualificationFlowDatum.product == quali_flow_data.product))\
               .delete()
        session.commit()
