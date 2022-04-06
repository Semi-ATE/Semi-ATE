from typing import Dict, List, Optional, Tuple

from ate_projectdatabase.Hardware.PingPong import PingPong, PingPongStage
from ate_projectdatabase.Utils import DB_KEYS, BaseType


DEFAULT_FIRST_PING_PONG_NAME = "All Parallel"


class ParallelismConfig:
    def __init__(self):
        self.name: str = None
        self.base_type: BaseType = None
        self.sites_count: int = None
        self.cells: Dict[int, Tuple(int, int)] = {}
        self.configs: List[PingPong[PingPongStage]] = []
        self.next_ping_pong_id: int = 0

    @staticmethod
    def new(name: str, base_type: BaseType, sites_count: int):
        obj = ParallelismConfig()
        obj.name = name
        assert isinstance(base_type, BaseType)
        obj.base_type = base_type
        obj.sites_count = sites_count
        obj._add_default_first_ping_pong()
        return obj

    def _add_default_first_ping_pong(self):
        self.add_ping_pong_config(DEFAULT_FIRST_PING_PONG_NAME, 1)
        self.configs[0].stages[0].stage = [site for site in range(self.sites_count)]

    @staticmethod
    def from_database(base_type: BaseType, data: Dict[str, any]) -> "ParallelismConfig":
        obj = ParallelismConfig()
        obj.name = data[DB_KEYS.HARDWARE.DEFINITION.PARALLELISM.NAME]
        obj.base_type = BaseType(base_type)
        obj.sites_count = len(data[DB_KEYS.HARDWARE.DEFINITION.PARALLELISM.SITES])

        for index, coord in enumerate(data[DB_KEYS.HARDWARE.DEFINITION.PARALLELISM.SITES]):
            obj.cells[index] = tuple(coord)
        for new_ping_pong in data[DB_KEYS.HARDWARE.DEFINITION.PARALLELISM.CONFIGS.KEY()]:
            obj.configs.append(PingPong.from_database(new_ping_pong))
        obj.next_ping_pong_id = data[DB_KEYS.HARDWARE.DEFINITION.PARALLELISM.NEXT_PING_PONG_ID]
        return obj

    def serialize(self) -> Dict[str, any]:
        return {
            DB_KEYS.HARDWARE.DEFINITION.PARALLELISM.NEXT_PING_PONG_ID: self.next_ping_pong_id,
            DB_KEYS.HARDWARE.DEFINITION.PARALLELISM.NAME: self.name,
            DB_KEYS.HARDWARE.DEFINITION.PARALLELISM.SITES: list(self.cells.values()),
            DB_KEYS.HARDWARE.DEFINITION.PARALLELISM.CONFIGS.KEY(): [ping_pong.serialize() for ping_pong in self.configs]
        }

    def are_all_sites_used(self) -> bool:
        return self.sites_count == len(self.cells)

    def add_ping_pong_config(self, name: str, stage_count: int):
        self.configs.append(PingPong(name, self.next_ping_pong_id, stage_count))
        self.next_ping_pong_id += 1

    def remove_ping_pong_config(self, rem_item: PingPong):
        if rem_item in self.configs:
            self.configs.remove(rem_item)

    def get_default_first_ping_pong(self) -> PingPong:
        if len(self.configs) == 0:
            self._add_default_first_ping_pong()
        return self.configs[0]

    def get_all_ping_pong_names(self) -> List[str]:
        return [ping_pong.name for ping_pong in self.configs]

    def get_ping_pong(self, name: str) -> Optional[PingPong]:
        for ping_pong in self.configs:
            if name == ping_pong.name:
                return ping_pong
        return None

    def get_ping_pong_by_id(self, id: int) -> Optional[PingPong]:
        for ping_pong in self.configs:
            if id == ping_pong.id:
                return ping_pong
        return None

    def are_all_configs_correct(self) -> Tuple[bool, Optional[str]]:
        for ping_pong in self.configs:
            all_sites = set()
            for st in ping_pong.stages:
                if not st.stage:
                    return False, f'{self.name}.{ping_pong.name} has an empty stage.'
                if all_sites.intersection(st.stage):
                    return False, f'{self.name}.{ping_pong.name}: A site can only be in one stage!'
                all_sites.update(st.stage)
            if len(all_sites) != self.sites_count:
                return False, f'{self.name}.{ping_pong.name} there are not all sites used.'
        return True, None
