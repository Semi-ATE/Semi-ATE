from typing import Dict, List, Set

from ate_projectdatabase.Utils import DB_KEYS


class PingPong:
    def __init__(self, name: str, id: int, stage_count: int):
        self.id: int = id
        self.name: str = name
        self.stages: List[PingPongStage] = []
        self.stage_count: int = stage_count

    @staticmethod
    def from_database(data: Dict[str, any]) -> "PingPong":
        """The dict should contain the following keys:
        DB_KEYS.HARDWARE.DEFINITION.PARALLELISM.CONFIGS.NAME with value of type "str"
        DB_KEYS.HARDWARE.DEFINITION.PARALLELISM.CONFIGS.STAGES with value of type "typing.List[typing.List[int]"
        """
        obj = PingPong(
            data[DB_KEYS.HARDWARE.DEFINITION.PARALLELISM.CONFIGS.NAME],
            data[DB_KEYS.HARDWARE.DEFINITION.PARALLELISM.CONFIGS.ID],
            0
        )
        for stage_data in data[DB_KEYS.HARDWARE.DEFINITION.PARALLELISM.CONFIGS.STAGES]:
            obj.stages.append(PingPongStage.from_database(stage_data))
        return obj

    def serialize(self) -> List[List[int]]:
        return {
            DB_KEYS.HARDWARE.DEFINITION.PARALLELISM.CONFIGS.ID: self.id,
            DB_KEYS.HARDWARE.DEFINITION.PARALLELISM.CONFIGS.NAME: self.name,
            DB_KEYS.HARDWARE.DEFINITION.PARALLELISM.CONFIGS.STAGES: [
                ping_pong_stage.serialize() for ping_pong_stage in self.stages
            ]
        }

    @property
    def stage_count(self) -> int:
        return len(self.stages)

    @stage_count.setter
    def stage_count(self, value: int):
        if value > self.stage_count:
            for _ in range(value - self.stage_count):
                self.stages.append(PingPongStage())
        elif value < self.stage_count:
            self.stages = self.stages[:value]

    def is_site_used(self, site_num):
        for st in self.stages:
            if site_num in st.stage:
                return True
        return False


class PingPongStage:
    def __init__(self):
        self.stage: Set[int] = set()

    @staticmethod
    def from_database(stage: List[str]) -> "PingPongStage":
        obj = PingPongStage()
        obj.stage = set([int(elem) for elem in stage])
        return obj

    def serialize(self) -> List[str]:
        return list([str(elem) for elem in self.stage])
