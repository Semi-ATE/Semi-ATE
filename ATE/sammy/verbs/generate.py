from ATE.sammy.verbs.verbbase import VerbBase
from ATE.projectdatabase.FileOperator import FileOperator


class Generate(VerbBase):
    def __init__(self, template_path):
        self.template_path = template_path

    def run(self, cwd: str, arglist) -> int:
        noun = arglist.noun

        valid_nouns = {"all": lambda: self.all(cwd, arglist),
                       "hardware": lambda: self.hardware(cwd, arglist),
                       "sequence": lambda: self.sequence(cwd, arglist),
                       "test": lambda: self.gen_tests(cwd, arglist),
                       "test_target": lambda: self.gen_test_targets(cwd, arglist),
                       "new": lambda: self.gen_new_project(cwd, arglist),
                       }

        if noun not in valid_nouns:
            print(f"    The noun '{noun}' is invalid in the context of generate.")
            return -1

        self.file_operator = FileOperator(cwd)

        return valid_nouns[noun]()

    def all(self, cwd: str, arglist: list):
        print("    Generate project")
        self.hardware(cwd, arglist)
        self.sequence(cwd, arglist)
        self.gen_tests(cwd, arglist)
        self.gen_test_targets(cwd, arglist)

    def gen_new_project(self, cwd: str, arglist: list):
        print("    Generate new project")
        from ATE.sammy.coding.generators import project_generator
        import os
        project_generator(self.template_path, os.path.join(cwd, arglist.params[0]))

    def sequence(self, cwd: str, arglist: list):
        print("    -> generate sequence(s)")
        from ATE.sammy.coding.ProgramGenerator import test_program_generator
        from ATE.projectdatabase.Sequence import Sequence
        from ATE.projectdatabase.TestTarget import TestTarget
        from ATE.projectdatabase.Program import Program

        programs = []
        if len(arglist.params) == 1:
            programs = [Program.get(self.file_operator, arglist.params[0])]
        else:
            programs = Program.get_all(self.file_operator)

        for program in programs:
            tests_in_program = Sequence.get_for_program(self.file_operator, program.prog_name)
            test_targets = TestTarget.get_for_program(self.file_operator, program.prog_name)
            program_configuration = Program.get_by_name_and_owner(self.file_operator, program.prog_name, program.owner_name)

            print(f"        gen {program.prog_name}")
            test_program_generator(self.template_path, cwd, program.prog_name, tests_in_program, test_targets, program_configuration)

        return 0

    def gen_tests(self, cwd: str, arglist: list):
        print("    -> generate test(s)")
        from ATE.sammy.coding.generators import test_generator, test_update
        from ATE.projectdatabase.Test import Test
        tests = []

        # params: name, hardware, base
        if len(arglist.params) == 3:
            tests = [Test.get(self.file_operator, arglist.params[0], arglist.params[1], arglist.params[2])]
        else:
            tests = Test.get_all(self.file_operator)

        for test in tests:
            print(f"        gen {test.name}")
            import os
            test_path = os.path.join(cwd, 'src', test.hardware, test.base, test.name)
            if not os.path.exists(test_path):
                test_generator(self.template_path, cwd, test.definition)
                continue

            test_update(self.template_path, cwd, test.definition)

        return 0

    def gen_test_targets(self, cwd: str, arglist: list):
        from ATE.sammy.coding.TargetGenerator import test_target_generator
        from ATE.projectdatabase.TestTarget import TestTarget
        from ATE.projectdatabase.Test import Test

        test_targets = []
        # params: target_name, test, hardware, base
        if len(arglist.params) == 4:
            test_targets = [TestTarget.get(self.file_operator, arglist.params[0], arglist.params[1], arglist.params[2], arglist.params[3])]
        else:
            test_targets = TestTarget.get_all(self.file_operator)

        for test_target in test_targets:
            import os
            test_path = os.path.join(cwd, 'src', test_target.hardware, test_target.base, test_target.name)
            testdefinition = Test.get(self.file_operator, test_target.test, test_target.hardware, test_target.base).definition
            testdefinition['base'] = test_target.base
            testdefinition['base_class'] = test_target.test
            testdefinition['name'] = test_target.name
            testdefinition['hardware'] = test_target.hardware

            if test_target.is_default:
                continue

            print(f"        gen {test_target.name}")
            if not os.path.exists(test_path):
                test_target_generator(self.template_path, cwd, testdefinition)
                continue

            test_target_generator(self.template_path, cwd, testdefinition, do_update=True)

    def hardware(self, cwd, arglist: list):
        print("    -> generate hardware")
        from ATE.sammy.coding.generators import hardware_generator
        from ATE.projectdatabase.Hardware import Hardware

        # check if we got a hwname, if so, we only generate this hardware:
        hws = []
        if len(arglist.params) == 1:
            hws = [Hardware.get(self.file_operator, arglist.params[0])]
        else:
            hws = Hardware.get_all(self.file_operator)

        for hw in hws:
            print(f"        gen {hw.name}")
            definition = self._prepare_hardware_definiton(hw.definition)
            definition["hardware"] = hw.name
            hardware_generator(self.template_path, cwd, definition)
        return 0

    def _prepare_hardware_definiton(self, definition):
        for index, hw in enumerate(definition['Actuator']['FT']):
            definition['Actuator']['FT'][index] = hw.replace(" ", "_")
        for index, hw in enumerate(definition['Actuator']['PR']):
            definition['Actuator']['PR'][index] = hw.replace(" ", "_")

        definition['InstrumentNames'] = {}
        for instrument in definition['Instruments']:
            definition['InstrumentNames'][instrument] = instrument.replace(" ", "_").replace(".", "_")

        definition['GPFunctionNames'] = {}

        for instrument in definition['GPFunctions']:
            definition['GPFunctionNames'][instrument] = instrument.replace(" ", "_").replace(".", "_")

        return definition
