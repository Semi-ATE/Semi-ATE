import os
import math

from ate_common.parameter import InputColumnKey, InputColumnLabel, OutputColumnKey, OutputColumnLabel
from ate_sammy.coding.BaseTestGenerator import BaseTestGenerator
from ate_sammy.coding.generator_utils import prepare_module_docstring


def prepare_input_parameters_table(ip):
    # """Generates a list of strings, holding a table (with header) of the input parameters"""

    retval = []
    name_ = 0
    Shmoo_ = 3  # True = Yes, False = No
    Min_ = 0
    Default_ = 0
    Max_ = 0
    Unit_ = 0
    fmt_ = 0
    for param in ip:
        if len(f"ip.{param}") > name_:
            name_ = len(f"ip.{param}")
    # Min --> number or -inf (no nan)
        if math.isinf(ip[param][InputColumnKey.MIN()]):
            length = len('-∞')
            if Min_ < length:
                Min_ = length
        elif math.isnan(ip[param][InputColumnKey.MIN()]):
            raise Exception(f"ip.{param}[{InputColumnKey.MIN()}] == math.nan ... not possible !")
        else:
            length = len(f"{ip[param][InputColumnKey.MIN()]:{ip[param][InputColumnKey.FMT()]}}")
            if Min_ < length:
                Min_ = length
    # Default --> number (no nan or inf)
        if math.isinf(ip[param][InputColumnKey.DEFAULT()]):
            raise Exception(f"ip.{param}[{InputColumnKey.DEFAULT()}] == ±math.inf ... not possible !")
        elif math.isnan(ip[param][InputColumnKey.DEFAULT()]):
            raise Exception(f"ip.{param}[{InputColumnKey.DEFAULT()}] == math.nan ... not possible !")
        else:
            length = len(f"{ip[param][InputColumnKey.DEFAULT()]:{ip[param][InputColumnKey.FMT()]}}")
            if Default_ < length:
                Default_ = length
    # Max --> number or inf (no nan)
        if math.isinf(ip[param][InputColumnKey.MAX()]):
            length = len('+∞')
            if Max_ < length:
                Max_ = length
        elif math.isnan(ip[param][InputColumnKey.MAX()]):
            raise Exception(f"ip.{param}[{InputColumnKey.MAX()}] == math.nan ... not possible !")
        else:
            length = len(f"{ip[param][InputColumnKey.MAX()]:{ip[param][InputColumnKey.FMT()]}}")
            if Max_ < length:
                Max_ = length
    # combined Unit
        length = len(f"{ip[param][InputColumnKey.POWER()]}{ip[param][InputColumnKey.UNIT()]}")
        if Unit_ < length:
            Unit_ = length
    # format
        length = len(f"{ip[param][InputColumnKey.FMT()]}")
        if fmt_ < length:
            fmt_ = length

    length = len('Input Parameter')
    if name_ < length:
        name_ = length

    length = len(InputColumnLabel.SHMOO())
    if Shmoo_ < length:
        Shmoo_ = length

    length = len(InputColumnLabel.MIN())
    if Min_ < length:
        Min_ = length

    length = len(InputColumnLabel.DEFAULT())
    if Default_ < length:
        Default_ = length

    length = len(InputColumnLabel.MAX())
    if Max_ < length:
        Max_ = length

    length = len(InputColumnLabel.UNIT())
    if Unit_ < length:
        Unit_ = length

    length = len(InputColumnLabel.FMT())
    if fmt_ < length:
        fmt_ = length

    th = f"{'Input Parameter':<{name_}} | "
    th += f"{InputColumnLabel.SHMOO():^{Shmoo_}} | "
    th += f"{InputColumnLabel.MIN():>{Min_}} | "
    th += f"{InputColumnLabel.DEFAULT():^{Default_}} | "
    th += f"{InputColumnLabel.MAX():<{Max_}} | "
    th += f"{InputColumnLabel.UNIT():<{Unit_}} | "
    th += f"{InputColumnLabel.FMT():<{fmt_}}"
    retval.append(th)

    bh = '-' * (name_ + 1) + '+'
    bh += '-' * (Shmoo_ + 2) + '+'
    bh += '-' * (Min_ + 2) + '+'
    bh += '-' * (Default_ + 2) + '+'
    bh += '-' * (Max_ + 2) + '+'
    bh += '-' * (Unit_ + 2) + '+'
    bh += '-' * (fmt_ + 1)
    retval.append(bh)

    for _, param in enumerate(ip):
        name = f"ip.{param}"
        Name = f"{name:{name_}} | "
    # Shmoo
        if ip[param][InputColumnKey.SHMOO()] is True:
            Shmoo = f"{'Yes':^{Shmoo_}} | "
        else:
            Shmoo = f"{'No':^{Shmoo_}} | "
    # Min
        if math.isinf(ip[param][InputColumnKey.MIN()]):
            Min = f"{'-∞':>{Min_}} | "
        else:
            Min = f"{ip[param][InputColumnKey.MIN()]:>{Min_}{ip[param][InputColumnKey.FMT()]}} | "
    # Default
        Default = f"{ip[param][InputColumnKey.DEFAULT()]:^{Default_}{ip[param][InputColumnKey.FMT()]}} | "
    # Max
        if math.isinf(ip[param][InputColumnKey.MAX()]):
            Max = f"{'+∞':<{Max_}} | "
        else:
            Max = f"{ip[param][InputColumnKey.MAX()]:<{Max_}{ip[param][InputColumnKey.FMT()]}} | "
    # Unit
        Unit = f"{ip[param][InputColumnKey.UNIT()]:<{Unit_}} | "
    # format
        Fmt = f"{ip[param][InputColumnKey.FMT()]:<{fmt_}}"

        line = Name + Shmoo + Min + Default + Max + Unit + Fmt
        retval.append(line)
    return retval


def prepare_output_parameters_table(op):
    """Generates a list of strings, holding a table (with header) of the output parameters"""
    retval = []
    name_ = 0
    LSL_ = 0
    LTL_ = 0
    Nom_ = 0
    UTL_ = 0
    USL_ = 0
    mul_ = 0
    unit_ = 0
    fmt_ = 0
    mpr_ = max([len('Yes'), len('No'), len(OutputColumnKey.MPR())])

    for param in op:
        if len(f"op.{param}") > name_:
            name_ = len(f"op.{param}")
    # LSL --> inf or number (no nan)
        if math.isinf(op[param][OutputColumnKey.LSL()]):
            if LSL_ < 2:
                LSL_ = 2  # len('-∞') = 2
        else:
            length = len(f"{op[param][OutputColumnKey.LSL()]:{op[param][OutputColumnKey.FMT()]}}")
            if LSL_ < length:
                LSL_ = length
    # LTL --> inf, nan or number
        if math.isinf(op[param][OutputColumnKey.LTL()]):
            if LTL_ < 2:
                LTL_ = 2  # len('-∞') = 2
        elif math.isnan(op[param][OutputColumnKey.LTL()]):
            if not math.isinf(op[param][OutputColumnKey.LSL()]):
                length = len(f"{op[param][OutputColumnKey.LSL()]:{op[param][OutputColumnKey.FMT()]}}") + 2  # the '()' around
                if LTL_ < length:
                    LTL_ = length
        else:
            length = len(f"{op[param][OutputColumnKey.LTL()]:{op[param][OutputColumnKey.FMT()]}}")
            if LTL_ < length:
                LTL_ = length
    # Nom --> number (no inf, no nan)
        length = len(f"{op[param][OutputColumnKey.NOM()]:{op[param][OutputColumnKey.FMT()]}}")
        if length > Nom_:
            Nom_ = length
    # UTL --> inf, nan or number
        if math.isinf(op[param][OutputColumnKey.UTL()]):
            if UTL_ < 2:
                UTL_ = 2
        elif math.isnan(op[param][OutputColumnKey.UTL()]):
            if not math.isinf(op[param][OutputColumnKey.USL()]):
                length = len(f"{op[param][OutputColumnKey.USL()]:{op[param][OutputColumnKey.FMT()]}}") + 2
                if UTL_ < length:
                    UTL_ = length
        else:
            length = len(f"{op[param][OutputColumnKey.UTL()]:{op[param][OutputColumnKey.FMT()]}}")
            if UTL_ < length:
                UTL_ = length
    # USL --> inf or number (not nan)
        if math.isinf(op[param][OutputColumnKey.USL()]):
            if 4 > USL_:
                USL_ = 4
        else:
            length = len(f"{op[param][OutputColumnKey.USL()]:{op[param][OutputColumnKey.FMT()]}}")
            if length > USL_:
                USL_ = length

        if len(f"{op[param][OutputColumnKey.POWER()]}") > mul_:
            mul_ = len(f"{op[param][OutputColumnKey.POWER()]}")

        if len(f"{op[param][OutputColumnKey.UNIT()]}") > unit_:
            unit_ = len(f"{op[param][OutputColumnKey.UNIT()]}")

        if len(f"{op[param][OutputColumnKey.FMT()]}") > fmt_:
            fmt_ = len(f"{op[param][OutputColumnKey.FMT()]}")

    length = len('Output Parameters')
    if name_ < length:
        name_ = length

    length = len(OutputColumnLabel.LSL())
    if LSL_ < length:
        LSL_ = length

    length = len(OutputColumnLabel.LTL())
    if LTL_ < length:
        LTL_ = length

    length = len(OutputColumnLabel.UTL())
    if UTL_ < length:
        UTL_ = length

    length = len(OutputColumnLabel.USL())
    if USL_ < length:
        USL_ = length

    Unit_ = mul_ + unit_
    length = len(OutputColumnLabel.UNIT())
    if Unit_ < length:
        Unit_ = length

    length = len(OutputColumnLabel.FMT())
    if fmt_ < length:
        fmt_ = length


    th = f"{'Parameter':<{name_}} | "
    th += f"{OutputColumnLabel.MPR():<{mpr_}} | "
    th += f"{OutputColumnLabel.LSL():>{LSL_}} | "
    th += f"{OutputColumnLabel.LTL():>{LTL_}} | "
    th += f"{OutputColumnLabel.NOM():^{Nom_}} | "
    th += f"{OutputColumnLabel.UTL():<{UTL_}} | "
    th += f"{OutputColumnLabel.USL():<{USL_}} | "
    th += f"{OutputColumnLabel.UNIT():<{Unit_}} | "
    th += f"{OutputColumnLabel.FMT():<{fmt_}}"
    retval.append(th)

    bh = '-' * (name_ + 1) + '+'
    bh += '-' * (mpr_ + 2) + '+'
    bh += '-' * (LSL_ + 2) + '+'
    bh += '-' * (LTL_ + 2) + '+'
    bh += '-' * (Nom_ + 2) + '+'
    bh += '-' * (UTL_ + 2) + '+'
    bh += '-' * (USL_ + 2) + '+'
    bh += '-' * (Unit_ + 2) + '+'
    bh += '-' * (fmt_ + 1)
    retval.append(bh)

    for _, param in enumerate(op):
        name = f"op.{param}"
        Name = f"{name:<{name_}} | "
    # MPR
        if op[param][OutputColumnKey.MPR()] is True:
            Mpr = f"{'Yes':^{mpr_}} | "
        else:
            Mpr = f"{'No':^{mpr_}} | "

    # LSL
        if math.isinf(op[param][OutputColumnKey.LSL()]):
            LSL = f"{'-∞':>{LSL_}} | "
        else:
            LSL = f"{op[param][OutputColumnKey.LSL()]:>{LSL_}{op[param][OutputColumnKey.FMT()]}} | "
    # LTL
        if math.isinf(op[param][OutputColumnKey.LTL()]):
            LTL = f"{'-∞':>{LTL_}} | "
        elif math.isnan(op[param][OutputColumnKey.LTL()]):
            if math.isinf(op[param][OutputColumnKey.LSL()]):
                LTL = f"{'(-∞)':>{LTL_}} | "
            else:
                ltl = f"({op[param][OutputColumnKey.LSL()]:{op[param][OutputColumnKey.FMT()]}})"
                LTL = f"{ltl:>{LTL_}} | "
        else:
            LTL = f"{op[param][OutputColumnKey.LTL()]:>{LTL_}{op[param][OutputColumnKey.FMT()]}} | "
    # Nom
        Nom = f"{op[param][OutputColumnKey.NOM()]:^{Nom_}{op[param][OutputColumnKey.FMT()]}} | "
    # UTL
        if math.isinf(op[param][OutputColumnKey.UTL()]):
            UTL = f"{'+∞':<{UTL_}} | "
        elif math.isnan(op[param][OutputColumnKey.UTL()]):
            if math.isinf(op[param][OutputColumnKey.USL()]):
                UTL = f"{'(+∞)':<{UTL_}} | "
            else:
                utl = f"({op[param][OutputColumnKey.USL()]:{op[param][OutputColumnKey.FMT()]}})"
                UTL = f"{utl:<{UTL_}} | "
        else:
            UTL = f"{op[param][OutputColumnKey.UTL()]:<{UTL_}{op[param][OutputColumnKey.FMT()]}} | "
    # USL
        if math.isinf(op[param][OutputColumnKey.USL()]):
            USL = f"{'+∞':<{USL_}} | "
        else:
            USL = f"{op[param][OutputColumnKey.USL()]:<{USL_}{op[param][OutputColumnKey.FMT()]}} | "
    # Unit
        Unit = f"{op[param][OutputColumnKey.UNIT()]:<{Unit_}} | "
    # format
        Fmt = f"{op[param][OutputColumnKey.FMT()]:<{fmt_}}"

        line = Name + Mpr + LSL + LTL + Nom + UTL + USL + Unit + Fmt
        retval.append(line)
    return retval


class test_proper_generator(BaseTestGenerator):
    """Generator for the Test Class."""

    do_not_touch_start = '<do_not_touch>'
    do_not_touch_end = '</do_not_touch>'

    def __init__(self, template_dir, project_path, definition, do_update=False):
        self.file_name = f"{definition['name']}.py"
        self.do_update = do_update
        super().__init__(template_dir, project_path, definition, self.file_name)

    def _generate_relative_path(self):
        hardware = self.definition['hardware']
        base = self.definition['base']
        name = self.definition['name']

        return self.project_path.joinpath(self.project_path.name, hardware, base, name)

    def _generate_render_data(self, abs_path=''):
        return {'module_doc_string': prepare_module_docstring(),
                'do_not_touch_section': self._generate_do_not_touch_section(),
                'definition': self.definition}

    def _render(self, template, render_data):
        return template.render(do_not_touch_section=render_data['do_not_touch_section'],
                               module_doc_string=render_data['module_doc_string'],
                               definition=self.definition)

    def _generate_do_not_touch_section(self):
        input_table_content = prepare_input_parameters_table(self.definition['input_parameters'])
        output_table_content = prepare_output_parameters_table(self.definition['output_parameters'])

        sec = '    ' + self.do_not_touch_start + '\n'
        if self.definition['patterns']:
            sec += '    ' + 'import Pattern class if missing' + '\n'
            sec += '    ' + f'  from {self.definition["name"]}_BC import Patterns' + '\n'
            sec += '    ' + 'get patterns id:' + '\n'

            for pattern in self.definition['patterns']:
                sec += '    ' + f'{pattern} = Patterns.{pattern} \n'

        for doc in self.definition['docstring'][0].split('\n'):
            sec += '    ' + doc + '\n'

        sec += self._stringify_table(input_table_content)
        sec += '\n'
        sec += self._stringify_table(output_table_content)
        sec += '    ' + self.do_not_touch_end + '\n'
        return sec

    @staticmethod
    def _stringify_table(table_content):
        table_str = ''
        for content in table_content:
            table_str += '    '
            table_str += content
            table_str += '\n'

        return table_str

    def _update_test_file(self):
        with open(self.abs_path_to_file, 'r') as f:
            content = f.readlines()

        start, end = self._find_do_not_touch_section(content)
        if start is None or end is None:
            # if do_no_touch section is missing !!!
            # TODO: should we raise an exception in this case ?
            return

        del content[start:end + 1]

        content.insert(start, self._generate_do_not_touch_section())
        with open(self.abs_path_to_file, 'w', encoding='utf-8') as f:
            for line in content:
                f.write(line)

    def _find_do_not_touch_section(self, contents):
        start, end = None, None
        for index, lines in enumerate(contents):
            if self.do_not_touch_start in lines:
                start = index

            if self.do_not_touch_end in lines:
                end = index

        return (start, end)

    def _generate(self, path, msg):
        if not self.do_update:
            super()._generate(path, msg)
        else:
            self._update_test_file()
