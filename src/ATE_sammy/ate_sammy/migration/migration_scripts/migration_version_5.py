import os

from ate_sammy.migration.migration_scripts.migrate_base import MigratorBase


DEFAUTL_PARLLELISMS = {
    "PR": {
        "next_ping_pong_id": 1,
        "name": "PR1A",
        "sites": [[0, 0]],
        "configs": [
            {
                "id": 0,
                "name": "All Parallel",
                "stages": [["0"]]
            }
        ]
    },
    "FT": {
        "next_ping_pong_id": 1,
        "name": "FT1A",
        "sites": [[0, 0]],
        "configs": [
            {
                "id": 0,
                "name": "All Parallel",
                "stages": [["0"]]
            }
        ]
    }
}


class MigrationVersion5(MigratorBase):
    def migrate_impl(self, defs_path: str) -> int:
        super().__init__()
        hw_path = os.path.join(defs_path, 'hardware')
        prog_path = os.path.join(defs_path, 'program')
        self.sequence_base_path = os.path.join(defs_path, 'sequence')
        self.migrate_section(hw_path, lambda path: self._migrate_parallelism_struct(path))
        self.migrate_section(hw_path, lambda path: self._migrate_hardware_definition(path))
        self.migrate_section(prog_path, lambda path: self._migrate_program(path))

        return 0

    def version_num(self) -> int:
        return 5

    def _migrate_parallelism_struct(self, file_name):
        """
        Change value of hardware.definition.Parallelism.configs
        configs: {} --> configs: []
        """
        hw = self.read_configuration(file_name)
        for single_hw in hw:
            parallelism_store = single_hw['definition']['Parallelism']
            if not parallelism_store:
                parallelism_store["PR"] = [DEFAUTL_PARLLELISMS['PR']]
                parallelism_store["FT"] = [DEFAUTL_PARLLELISMS['FT']]
                continue
            for base_type, configs in parallelism_store.items():
                if not configs:
                    parallelism_store[base_type] = DEFAUTL_PARLLELISMS[base_type]
                    continue
                for config in configs:
                    if 'configs' not in config:
                        config['configs'] = []
                    if 'next_ping_pong_id' not in config:
                        config['next_ping_pong_id'] = len(config['configs'])
                    for index, ping_pong in enumerate(config['configs']):
                        if 'id' not in ping_pong:
                            ping_pong['id'] = index
        self.write_configuration(file_name, hw)

    def _migrate_hardware_definition(self, file_name):
        """
        Remove obsolte keys from database:
            - InstrumentNames
            - GPFunctionNames
        And in the Actuators convert underline to spaces
        """
        hw = self.read_configuration(file_name)
        for single_hw in hw:
            definition = single_hw['definition']
            if 'InstrumentNames' in definition:
                del definition['InstrumentNames']
            if 'GPFunctionNames' in definition:
                del definition['GPFunctionNames']

            definition['Actuator']['PR'] = [
                val.replace("_", " ") for val in definition['Actuator']['PR']
            ]
            definition['Actuator']['FT'] = [
                val.replace("_", " ") for val in definition['Actuator']['FT']
            ]

        self.write_configuration(file_name, hw)

    def _migrate_program(self, file_name):
        """
        Add new keys to program:
            instance_count
            execution_sequence
        """
        prog_list = self.read_configuration(file_name)
        for prog in prog_list:
            seq_path = os.path.join(self.sequence_base_path, f"sequence{prog['prog_name']}.json")
            seq_data = self.read_configuration(seq_path)
            if "instance_count" not in prog:
                prog["instance_count"] = len(seq_data)
            if "execution_sequence" not in prog:
                base = prog["base"]
                prog["execution_sequence"] = {
                    DEFAUTL_PARLLELISMS[base]['name']: [
                        0 for _ in range(len(seq_data))
                    ]
                }

        self.write_configuration(file_name, prog_list)
