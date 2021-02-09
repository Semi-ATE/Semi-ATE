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
                       "test": lambda: self.gen_tests(cwd, arglist)
                       }

        if noun not in valid_nouns:
            print(f"    The noun '{noun}' is invalid in the context of generate.")
            return -1

        self.file_operator = FileOperator(cwd)

        return valid_nouns[noun]()

    def all(self, cwd, arglist: list):
        print("    Regenerate project")
        self.hardware(cwd, arglist)
        self.sequence(cwd, arglist)
        self.sequence(cwd, arglist)
        self.gen_tests(cwd, arglist)

    def sequence(self, cwd, arglist: list):
        pass

    def gen_tests(self, cwd, arglist: list):
        pass

    def hardware(self, cwd, arglist: list):
        print("    ->regenerate hardware")
        from ATE.sammy.coding.generators import hardware_generator
        from ATE.projectdatabase.Hardware import Hardware

        # check if we got a hwname, if so, we only generate this hardware:
        hws = []
        if len(arglist.params) == 1:
            hws = [Hardware.get(self.file_operator, arglist.params[0])]
        else:
            hws = Hardware.get_all(self.file_operator)

        for hw in hws:
            print(f"        regen {hw.name}")
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
