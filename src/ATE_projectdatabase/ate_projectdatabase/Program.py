from typing import Dict, List
from ate_projectdatabase.Types import Types
from ate_projectdatabase.FileOperator import DBObject, FileOperator
from uuid import uuid1

ExecutionSequenceType = Dict[str, List[int]]


class Program:

    @staticmethod
    def add(
        session: FileOperator, name: str, hardware: str, base: str, target: str, usertext: str,
        sequencer_typ: str, temperature: str, owner_name: str, order: int, cache_type: str,
        caching_policy: str, test_ranges: list, instance_count: int, execution_sequence: ExecutionSequenceType
    ):
        prog = {
            "id": str(uuid1()), "prog_name": name, "hardware": hardware, "base": base, "target": target, "usertext": usertext,
            "sequencer_type": sequencer_typ, "temperature": temperature, "owner_name": owner_name, "prog_order": order,
            "is_valid": True, "cache_type": cache_type, "caching_policy": caching_policy, "test_ranges": test_ranges,
            "instance_count": instance_count, "execution_sequence": execution_sequence
        }
        session.query(Types.Program()).add(prog)
        session.commit()

    @staticmethod
    def update(
        session: FileOperator, name: str, hardware: str, base: str, target: str, usertext: str,
        sequencer_type: str, temperature: str, owner_name: str, cache_type: str, caching_policy: str,
        test_ranges: list, instance_count: int, execution_sequence: ExecutionSequenceType
    ):
        prog = Program.get_by_name_and_owner(session, name, owner_name)
        prog.hardware = hardware
        prog.base = base
        prog.target = target
        prog.usertext = usertext
        prog.sequencer_type = sequencer_type
        prog.temperature = temperature
        prog.cache_type = cache_type
        prog.caching_policy = caching_policy
        prog.test_ranges = test_ranges
        prog.instance_count = instance_count
        prog.execution_sequence = execution_sequence
        session.commit()

    @staticmethod
    def remove(session: FileOperator, program_name: str, owner_name: str):
        session.query(Types.Program())\
               .filter(lambda Program: (Program.prog_name == program_name and Program.owner_name == owner_name))\
               .delete()
        session.commit()

    @staticmethod
    def get(session: FileOperator, name: str) -> DBObject:
        return session.query(Types.Program())\
                      .filter(lambda Program: Program.prog_name == name)\
                      .one()

    @staticmethod
    def get_by_name_and_owner(session: FileOperator, prog_name: str, owner_name: str) -> DBObject:
        return session.query(Types.Program())\
                      .filter(lambda Program: (Program.prog_name == prog_name and Program.owner_name == owner_name))\
                      .one()

    @staticmethod
    def get_by_order_and_owner(session: FileOperator, prog_order: str, owner_name: str) -> DBObject:
        return session.query(Types.Program())\
                      .filter(lambda Program: (Program.prog_order == prog_order and Program.owner_name == owner_name))\
                      .one()

    @staticmethod
    def update_program_name(session: FileOperator, prog_name: str, new_name: str):
        prog = Program.get(session, prog_name)
        prog.prog_name = new_name
        session.commit()

    @staticmethod
    def _update_program_order_neighbour(session: FileOperator, owner_name: str, prev_order: int, order: int, new_name: str, id: int):
        prog = session.query(Types.Program())\
                      .filter(lambda Program: (Program.owner_name == owner_name and Program.prog_order == prev_order and Program.id != id))\
                      .one()
        prog.prog_order = order
        prog.prog_name = new_name
        session.commit()

    @staticmethod
    def _update_program_order(session: FileOperator, owner_name: str, prev_order: int, order: int, new_name: str):
        prog = session.query(Types.Program())\
                      .filter(lambda Program: (Program.owner_name == owner_name and Program.prog_order == prev_order))\
                      .one()
        prog.prog_name = new_name
        prog.prog_order = order
        session.commit()

    def update_program_order(session: FileOperator, program_name: str, owner_name: str, order: int):
        program = session.query(Types.Program())\
                         .filter(lambda Program: Program.prog_name == program_name and Program.owner_name == owner_name)\
                         .one()
        program.prog_order = order
        session.commit()

    @staticmethod
    def get_programs_for_owner(session: FileOperator, owner_name: str) -> list:
        return session.query(Types.Program())\
                      .filter(lambda Program: Program.owner_name == owner_name).sort(lambda Program: Program.prog_order)\
                      .all()

    @staticmethod
    def get_all(session: FileOperator) -> List[DBObject]:
        return session.query(Types.Program())\
                      .all()

    @staticmethod
    def get_program_owner_element_count(session: FileOperator, owner_name: str) -> int:
        return session.query(Types.Program())\
                      .filter(lambda Program: Program.owner_name == owner_name)\
                      .count()

    @staticmethod
    def get_programs_for_hardware(session: FileOperator, hardware: str) -> List[DBObject]:
        return session.query(Types.Program())\
                      .filter(lambda Program: Program.hardware == hardware)\
                      .sort(lambda Program: Program.prog_order)\
                      .all()

    @staticmethod
    def update_program_order(session: FileOperator, new_order: int, owner_name: str, current_order: int):
        prog = Program.get_by_order_and_owner(session, current_order, owner_name)
        prog.prog_order = new_order
        session.commit()

    @staticmethod
    def get_programs_for_target(session: FileOperator, target_name: str) -> list:
        return session.query(Types.Program())\
                      .filter(lambda Program: (Program.target == target_name))\
                      .all()

    @staticmethod
    def get_program_execution_sequence(session: FileOperator, program_name: str) -> ExecutionSequenceType:
        cur_obj = Program.get(session, program_name)
        return cur_obj.execution_sequence

    @staticmethod
    def get_ping_pong_in_executions(session: FileOperator, parallelism_name: str, ping_pong_id: int) -> List[str]:
        ret = []
        for x in Program.get_all(session):
            if ping_pong_id in x.execution_sequence[parallelism_name]:
                ret.append(x.name)
        return ret

    @staticmethod
    def add_parallelism_to_execution_sequence(session: FileOperator, hardware: str, parallelism_name: str, ping_pong_id: int):
        for x in Program.get_programs_for_hardware(session, hardware):
            x.execution_sequence[parallelism_name] = [ping_pong_id for _ in range(x.instance_count)]
        session.commit()

    @staticmethod
    def remove_parallelism_from_execution_sequence(session: FileOperator, hardware: str, parallelism_name: str):
        for x in Program.get_programs_for_hardware(session, hardware):
            del x.execution_sequence[parallelism_name]
        session.commit()

    @staticmethod
    def set_program_validity(session: FileOperator, name: str, is_valid: bool):
        program = Program.get(session, name)
        program.is_valid = is_valid
        session.commit()
