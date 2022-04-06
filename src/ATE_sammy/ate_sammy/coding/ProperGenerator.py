import os
import math

from ate_sammy.coding.BaseTestGenerator import BaseTestGenerator
from ate_sammy.coding.generator_utils import prepare_module_docstring


def prepare_input_parameters_table(ip):
    # """Generates a list of strings, holding a talble (with header) of the input parameters"""

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
        if math.isinf(ip[param]['Min']):
            length = len('-∞')
            if Min_ < length:
                Min_ = length
        elif math.isnan(ip[param]['Min']):
            raise Exception(f"ip.{param}['Min'] == math.nan ... not possible !")
        else:
            length = len(f"{ip[param]['Min']:{ip[param]['fmt']}}")
            if Min_ < length:
                Min_ = length
    # Default --> number (no nan or inf)
        if math.isinf(ip[param]['Default']):
            raise Exception(f"ip.{param}['Default'] == ±math.inf ... not possible !")
        elif math.isnan(ip[param]['Default']):
            raise Exception(f"ip.{param}['Default'] == math.nan ... not possible !")
        else:
            length = len(f"{ip[param]['Default']:{ip[param]['fmt']}}")
            if Default_ < length:
                Default_ = length
    # Max --> number or inf (no nan)
        if math.isinf(ip[param]['Max']):
            length = len('+∞')
            if Max_ < length:
                Max_ = length
        elif math.isnan(ip[param]['Max']):
            raise Exception(f"ip.{param}['Max'] == math.nan ... not possible !")
        else:
            length = len(f"{ip[param]['Max']:{ip[param]['fmt']}}")
            if Max_ < length:
                Max_ = length
    # combined Unit
        length = len(f"{ip[param]['10ᵡ']}{ip[param]['Unit']}")
        if Unit_ < length:
            Unit_ = length
    # format
        length = len(f"{ip[param]['fmt']}")
        if fmt_ < length:
            fmt_ = length

    length = len('Input Parameter')
    if name_ < length:
        name_ = length

    length = len('Shmoo')
    if Shmoo_ < length:
        Shmoo_ = length

    length = len('Min')
    if Min_ < length:
        Min_ = length

    length = len('Default')
    if Default_ < length:
        Default_ = length

    length = len('Max')
    if Max_ < length:
        Max_ = length

    length = len('Unit')
    if Unit_ < length:
        Unit_ = length

    length = len('fmt')
    if fmt_ < length:
        fmt_ = length

    th = f"{'Input Parameter':<{name_}} | "
    th += f"{'Shmoo':^{Shmoo_}} | "
    th += f"{'Min':>{Min_}} | "
    th += f"{'Default':^{Default_}} | "
    th += f"{'Max':<{Max_}} | "
    th += f"{'Unit':>{Unit_}} | "
    th += f"{'fmt':>{fmt_}}"
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
        if ip[param]['Shmoo'] is True:
            Shmoo = f"{'Yes':^{Shmoo_}} | "
        else:
            Shmoo = f"{'No':^{Shmoo_}} | "
    # Min
        if math.isinf(ip[param]['Min']):
            Min = f"{'-∞':>{Min_}} | "
        else:
            Min = f"{ip[param]['Min']:>{Min_}{ip[param]['fmt']}} | "
    # Default
        Default = f"{ip[param]['Default']:^{Default_}{ip[param]['fmt']}} | "
    # Max
        if math.isinf(ip[param]['Max']):
            Max = f"{'+∞':<{Max_}} | "
        else:
            Max = f"{ip[param]['Max']:<{Max_}{ip[param]['fmt']}} | "
    # Unit
        Unit = f"{ip[param]['Unit']} | "
    # format
        Fmt = f"{ip[param]['fmt']:<{fmt_}}"

        line = Name + Shmoo + Min + Default + Max + Unit + Fmt
        retval.append(line)
    return retval


def prepare_output_parameters_table(op):
    """Generates a list of strings, holding a talble (with header) of the output parameters"""
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
    for param in op:
        if len(f"op.{param}") > name_:
            name_ = len(f"op.{param}")
    # LSL --> inf or number (no nan)
        if math.isinf(op[param]['LSL']):
            if LSL_ < 2:
                LSL_ = 2  # len('-∞') = 2
        else:
            length = len(f"{op[param]['LSL']:{op[param]['fmt']}}")
            if LSL_ < length:
                LSL_ = length
    # LTL --> inf, nan or number
        if math.isinf(op[param]['LTL']):
            if LTL_ < 2:
                LTL_ = 2  # len('-∞') = 2
        elif math.isnan(op[param]['LTL']):
            if not math.isinf(op[param]['LSL']):
                length = len(f"{op[param]['LSL']:{op[param]['fmt']}}") + 2  # the '()' around
                if LTL_ < length:
                    LTL_ = length
        else:
            length = len(f"{op[param]['LTL']:{op[param]['fmt']}}")
            if LTL_ < length:
                LTL_ = length
    # Nom --> number (no inf, no nan)
        length = len(f"{op[param]['Nom']:{op[param]['fmt']}}")
        if length > Nom_:
            Nom_ = length
    # UTL --> inf, nan or number
        if math.isinf(op[param]['UTL']):
            if UTL_ < 2:
                UTL_ = 2
        elif math.isnan(op[param]['UTL']):
            if not math.isinf(op[param]['USL']):
                length = len(f"{op[param]['USL']:{op[param]['fmt']}}") + 2
                if UTL_ < length:
                    UTL_ = length
        else:
            length = len(f"{op[param]['UTL']:{op[param]['fmt']}}")
            if UTL_ < length:
                UTL_ = length
    # USL --> inf or number (not nan)
        if math.isinf(op[param]['USL']):
            if 4 > USL_:
                USL_ = 4
        else:
            length = len(f"{op[param]['USL']:{op[param]['fmt']}}")
            if length > USL_:
                USL_ = length

        if len(f"{op[param]['10ᵡ']}") > mul_:
            mul_ = len(f"{op[param]['10ᵡ']}")

        if len(f"{op[param]['Unit']}") > unit_:
            unit_ = len(f"{op[param]['Unit']}")

        if len(f"{op[param]['fmt']}") > fmt_:
            fmt_ = len(f"{op[param]['fmt']}")

    length = len('Output Parameters')
    if name_ < length:
        name_ = length

    length = len('LSL')
    if LSL_ < length:
        LSL_ = length

    length = len('(LTL)')
    if LTL_ < length:
        LTL_ = length

    length = len('(UTL)')
    if UTL_ < length:
        UTL_ = length

    length = len('USL')
    if USL_ < length:
        USL_ = length

    Unit_ = mul_ + unit_
    length = len('Unit')
    if Unit_ < length:
        Unit_ = length

    length = len('fmt')
    if fmt_ < length:
        fmt_ = length

    th = f"{'Parameter':<{name_}} | "
    th += f"{'LSL':>{LSL_}} | "
    th += f"{'(LTL)':>{LTL_}} | "
    th += f"{'Nom':^{Nom_}} | "
    th += f"{'(UTL)':<{UTL_}} | "
    th += f"{'USL':<{USL_}} | "
    th += f"{'Unit':>{Unit_}} | "
    th += f"{'fmt':>{fmt_}}"
    retval.append(th)

    bh = '-' * (name_ + 1) + '+'
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
    # LSL
        if math.isinf(op[param]['LSL']):
            LSL = f"{'-∞':>{LSL_}} | "
        else:
            LSL = f"{op[param]['LSL']:>{LSL_}{op[param]['fmt']}} | "
    # LTL
        if math.isinf(op[param]['LTL']):
            LTL = f"{'-∞':>{LTL_}} | "
        elif math.isnan(op[param]['LTL']):
            if math.isinf(op[param]['LSL']):
                LTL = f"{'(-∞)':>{LTL_}} | "
            else:
                ltl = f"({op[param]['LSL']:{op[param]['fmt']}})"
                LTL = f"{ltl:>{LTL_}} | "
        else:
            LTL = f"{op[param]['LTL']:>{LTL_}{op[param]['fmt']}} | "
    # Nom
        Nom = f"{op[param]['Nom']:^{Nom_}{op[param]['fmt']}} | "
    # UTL
        if math.isinf(op[param]['UTL']):
            UTL = f"{'+∞':<{UTL_}} | "
        elif math.isnan(op[param]['UTL']):
            if math.isinf(op[param]['USL']):
                UTL = f"{'(+∞)':<{UTL_}} | "
            else:
                utl = f"({op[param]['USL']:{op[param]['fmt']}})"
                UTL = f"{utl:<{UTL_}} | "
        else:
            UTL = f"{op[param]['UTL']:<{UTL_}{op[param]['fmt']}} | "
    # USL
        if math.isinf(op[param]['USL']):
            USL = f"{'+∞':<{USL_}} | "
        else:
            USL = f"{op[param]['USL']:<{USL_}{op[param]['fmt']}} | "
    # Unit
        Unit = f"{op[param]['Unit']} | "
    # format
        Fmt = f"{op[param]['fmt']:<{fmt_}}"

        line = Name + LSL + LTL + Nom + UTL + USL + Unit + Fmt
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

        return os.path.join('src', hardware, base, name)

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

        for doc in self.definition['docstring'][0].split('\n'):
            sec += '    ' + doc + '\n'

        sec += '\n\n'
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
