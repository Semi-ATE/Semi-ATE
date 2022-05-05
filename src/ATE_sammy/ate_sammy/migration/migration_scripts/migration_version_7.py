import os

from ate_sammy.migration.migration_scripts.migrate_base import MigratorBase
from ate_common.parameter import InputColumnKey, OutputColumnKey


class MigrationVersion7(MigratorBase):
    def migrate_impl(self, defs_path: str) -> int:
        super().__init__()
        prog_path = os.path.join(defs_path, 'program')
        self.sequence_base_path = os.path.join(defs_path, 'sequence')
        self.migrate_section(prog_path, lambda path: self._migrate_program(path))

        test_path = os.path.join(defs_path, 'test')
        # self.sequence_base_path = os.path.join(defs_path, 'sequence')
        self.migrate_section(test_path, lambda path: self._migrate_test(path))
        return 0

    def version_num(self) -> int:
        return 7

    def _migrate_test(self, file_name):
        tests = self.read_configuration(file_name)
        for test_data in tests:
            for _, input in test_data['definition']['input_parameters'].items():
                value = input['Shmoo']
                input.pop('Shmoo')    
                input[InputColumnKey.SHMOO()] = value
                
                value = input['Min']
                input.pop('Min')    
                input[InputColumnKey.MIN()] = value

                value = input['Default']
                input.pop('Default')    
                input[InputColumnKey.DEFAULT()] = value

                value = input['Max']
                input.pop('Max')
                input[InputColumnKey.MAX()] = value

                value = input['10ᵡ']
                input.pop('10ᵡ')
                input[InputColumnKey.POWER()] = value

                value = input['Unit']
                input.pop('Unit')
                input[InputColumnKey.UNIT()] = value

                value = input['fmt']
                input.pop('fmt')
                input[InputColumnKey.FMT()] = value

            for _, output in test_data['definition']['output_parameters'].items():
                value = output['LSL']
                output.pop('LSL')
                output[OutputColumnKey.LSL()] = value

                value = output['LTL']
                output.pop('LTL')
                output[OutputColumnKey.LTL()] = value

                value = output['Nom']
                output.pop('Nom')
                output[OutputColumnKey.NOM()] = value

                value = output['UTL']
                output.pop('UTL')
                output[OutputColumnKey.UTL()] = value

                value = output['USL']
                output.pop('USL')
                output[OutputColumnKey.USL()] = value

                value = output['10ᵡ']
                output.pop('10ᵡ')
                output[OutputColumnKey.POWER()] = value

                value = output['Unit']
                output.pop('Unit')
                output[OutputColumnKey.UNIT()] = value

                value = output['fmt']
                output.pop('fmt')
                output[OutputColumnKey.FMT()] = value

                # add the new introduced mpr attribute with default value equal to false
                output[OutputColumnKey.MPR()] = False


        self.write_configuration(file_name, tests)


    def _migrate_program(self, file_name):
        prog_list = self.read_configuration(file_name)
        for prog in prog_list:
            seq_path = os.path.join(self.sequence_base_path, f"sequence{prog['prog_name']}.json")
            seq_data = self.read_configuration(seq_path)

            for _, test_config in enumerate(seq_data):
                for _, input in test_config['definition']['input_parameters'].items():

                    value = input['Shmoo']
                    input.pop('Shmoo')
                    input[InputColumnKey.SHMOO()] = value

                    value = input['Min']
                    input.pop('Min')
                    input[InputColumnKey.MIN()] = value

                    value = input['Default']
                    input.pop('Default')
                    input[InputColumnKey.DEFAULT()] = value

                    value = input['Max']
                    input.pop('Max')
                    input[InputColumnKey.MAX()] = value

                    value = input['10ᵡ']
                    input.pop('10ᵡ')
                    input[InputColumnKey.POWER()] = value

                    value = input['Unit']
                    input.pop('Unit')
                    input[InputColumnKey.UNIT()] = value

                    value = input['fmt']
                    input.pop('fmt')
                    input[InputColumnKey.FMT()] = value


                for _, output in test_config['definition']['output_parameters'].items():

                    value = output['LSL']
                    output.pop('LSL')
                    output[OutputColumnKey.LSL()] = value

                    value = output['LTL']
                    output.pop('LTL')
                    output[OutputColumnKey.LTL()] = value

                    value = output['UTL']
                    output.pop('UTL')
                    output[OutputColumnKey.UTL()] = value

                    value = output['USL']
                    output.pop('USL')
                    output[OutputColumnKey.USL()] = value

                    value = output['10ᵡ']
                    output.pop('10ᵡ')
                    output[OutputColumnKey.POWER()] = value

                    value = output['Unit']
                    output.pop('Unit')
                    output[OutputColumnKey.UNIT()] = value

                    value = output['fmt']
                    output.pop('fmt')
                    output[OutputColumnKey.FMT()] = value


            self.write_configuration(seq_path, seq_data)
