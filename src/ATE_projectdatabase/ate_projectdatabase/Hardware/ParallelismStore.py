
from typing import Dict, List, Optional, Tuple

from ate_projectdatabase.Hardware.ParallelismConfig import ParallelismConfig

from ate_projectdatabase.Utils import BaseType


class ParallelismStore:
    def __init__(self):
        self.parallelism_store: Dict[str, ParallelismConfig] = {}

    @staticmethod
    def from_database(parallelism_data: Dict[str, any]) -> "ParallelismStore":
        obj = ParallelismStore()
        for base_type, configs in parallelism_data.items():
            for table in configs:
                obj.add(ParallelismConfig.from_database(base_type, table))
        return obj

    def serialize(self) -> Dict[str, List[any]]:
        serialize = {
            BaseType.PR.value: [],
            BaseType.FT.value: []
        }
        for config_table in self.parallelism_store.values():
            if config_table.base_type == BaseType.PR:
                serialize[BaseType.PR.value].append(config_table.serialize())
            elif config_table.base_type == BaseType.FT:
                serialize[BaseType.FT.value].append(config_table.serialize())
        return serialize

    def add(self, config: ParallelismConfig):
        self.parallelism_store[config.name] = config

    def remove(self, name: str):
        self.parallelism_store.pop(name)

    def get(self, name: str) -> ParallelismConfig:
        return self.parallelism_store[name]

    def add_all(self, new_data: List[ParallelismConfig]):
        for table_obj in new_data:
            self.add(table_obj)

    def get_all_matching_base(self, base_type: BaseType) -> Dict[str, ParallelismConfig]:
        return {
            name: config for name, config in self.parallelism_store.items()
            if config.base_type == BaseType(base_type)
        }

    def get_all(self) -> Dict[str, ParallelismConfig]:
        return self.parallelism_store

    def get_count_matching_base(self, base_type: BaseType) -> int:
        return len(self.get_all_matching_base(base_type).keys())

    def all_tables_filled(self) -> bool:
        for table in self.parallelism_store.values():
            if not table.are_all_sites_used():
                return False
        return True

    @staticmethod
    def gen_suffix(num) -> str:
        letter_offset = ord('A')
        suffix = ''
        while num >= 26:
            letter = num % 26
            num = num // 26 - 1
            suffix += chr(letter_offset + letter)
        suffix += chr(letter_offset + num)
        return suffix[::-1]

    def generate_next_config_name(self, base_type: BaseType, add_sites_count: int):
        new_name = base_type.value + str(add_sites_count)
        name_suffix_num = 0
        name_suffix = ParallelismStore.gen_suffix(name_suffix_num)
        while str(new_name + name_suffix) in self.parallelism_store:
            name_suffix_num += 1
            name_suffix = ParallelismStore.gen_suffix(name_suffix_num)
        new_name += name_suffix
        return new_name

    def find_duplicate(self) -> Tuple[bool, Optional[str], Optional[str]]:
        index_pairs = [(a, b) for a in range(len(self.parallelism_store)) for b in range(a)]
        key_list = list(self.parallelism_store.keys())
        for (a, b) in index_pairs:
            if ParallelismStore.does_pattern_match(
                self.parallelism_store[key_list[a]],
                self.parallelism_store[key_list[b]]
            ):
                return True, key_list[a], key_list[b]
        return False, None, None

    @staticmethod
    def does_pattern_match(table_1: ParallelismConfig, table_2: ParallelismConfig) -> bool:
        if (len(table_1.cells) != len(table_2.cells)
                or table_1.base_type != table_2.base_type):
            return False
        if table_1 == table_2:
            return True
        for site_num, coord in table_1.cells.items():
            if table_2.cells[site_num] != coord:
                return False
        return True

    def min_required_parallelism(self) -> int:
        value = 0
        for table in self.parallelism_store.values():
            if table.sites_count > value:
                value = table.sites_count
        return value
