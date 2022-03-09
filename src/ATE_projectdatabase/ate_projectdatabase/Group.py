from ate_projectdatabase.Types import Types
from ate_projectdatabase.FileOperator import DBObject, FileOperator


class Group:
    @staticmethod
    def get(session: FileOperator, name: str) -> DBObject:
        return session.query(Types.Group())\
                      .filter(lambda Group: Group.name == name)\
                      .one()

    @staticmethod
    def get_all(session: FileOperator) -> DBObject:
        return session.query(Types.Group()).all()

    @staticmethod
    def add(session: FileOperator, name: str, is_standard: bool = False):
        group = {"name": name, "is_selected": True, "is_standard": is_standard, "programs": [], "tests": []}
        session.query(Types.Group()).add(group)
        session.commit()

    @staticmethod
    def update_state(session: FileOperator, name: str, is_selected: bool):
        group = session.query(Types.Group()).filter(lambda Group: Group.name == name).one()
        group.is_selected = is_selected
        session.commit()

    @staticmethod
    def remove(session: FileOperator, name: str):
        session.query(Types.Group())\
               .filter(lambda Group: Group.name == name)\
               .delete()
        session.commit()

    @staticmethod
    def is_standard(session: FileOperator, name: str) -> bool:
        group = session.query(Types.Group()).filter(lambda Group: Group.name == name).one()
        return group.is_standard

    @staticmethod
    def add_testprogram_to_group(session: FileOperator, group: str, prog_name: str):
        group = session.query(Types.Group()).filter(lambda Group: Group.name == group).one()
        group.programs.append(prog_name)
        session.commit()

    @staticmethod
    def remove_testprogram_from_group(session: FileOperator, group: str, prog_name: str):
        group = session.query(Types.Group()).filter(lambda Group: Group.name == group).one()
        group.programs.pop(group.programs.index(prog_name))
        session.commit()

    @staticmethod
    def remove_test_from_group(session: FileOperator, group: str, test: str):
        group = session.query(Types.Group()).filter(lambda Group: Group.name == group).one()
        group.tests.pop(group.tests.index(test))
        session.commit()

    @staticmethod
    def get_programs_for_group(session: FileOperator, group: str) -> list:
        group = session.query(Types.Group()).filter(lambda Group: Group.name == group).one()
        return group.programs

    @staticmethod
    def get_all_groups_for_test(session: FileOperator, test_name: str):
        return session.query(Types.Group()).filter(lambda Group: test_name in Group.tests).all()

    @staticmethod
    def update_groups_for_test(session: FileOperator, test: str, groups: list):
        all_groups_contains_test = Group.get_all_groups_for_test(session, test)
        for group_name in groups:
            group = session.query(Types.Group()).filter(lambda Group: Group.name == group_name).one()
            if test in group.tests:
                continue

            group.tests.append(test)

        if [group.name for group in all_groups_contains_test] != groups:
            # remove from list if needed
            for group in all_groups_contains_test:
                if group.name in groups:
                    continue

                group.tests.pop(group.tests.index(test))

        session.commit()

    @staticmethod
    def add_test_to_group(session: FileOperator, group: str, test: str):
        group = session.query(Types.Group()).filter(lambda Group: Group.name == group).one()
        group.tests.append(test)
        session.commit()

    @staticmethod
    def get_tests_for_group(session: FileOperator, group: str):
        group = session.query(Types.Group()).filter(lambda Group: Group.name == group).one()
        return group.tests
