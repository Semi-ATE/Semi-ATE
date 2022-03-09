from enum import Enum


DEFINITION = {'WaferDiameter': None,
              'Bondpads': None,
              'DieSize': None,
              'DieRef': None,
              'Offset': None,
              'Scribe': None,
              'Flat': None,
              'BondpadTable': None,  # template {1: ('bondpad1name', 100, 100, 90, 90),
                                     #           2: ('bondpad2name', -100, -100, 90, 90)},
              'Wafermap': None}      # {'rim': [(100, 80), (-80, -100)],
                                     # 'blank': [(80, 80)],
                                     # 'test_insert': [],
                                     # 'unused': []}}


class PadType(Enum):
    Digital = ('D', 'Digital')
    Analog = ('A', 'Analog')
    Mixed = ('M', 'Mixed')
    Power = ('P', 'Power')

    def __call__(self):
        return self.value


class PadDirection(Enum):
    Input = ('I', 'Input')
    Output = ('O', 'Output')
    Bidirectional = ('IO', 'Bidirectional')

    def __call__(self):
        return self.value


class PadStandardSize(Enum):
    Standard_1 = ('80', '80 x 80')
    Standard_2 = ('90', '90 x 90')
    Standard_3 = ('100', '100 x 100')

    def __call__(self):
        return self.value


DEFAULT_ROW = ['', 0, 0, '100', '100', PadType.Analog()[0], PadDirection.Input()[0]]


class PAD_INFO(Enum):
    PAD_NAME_COLUMN = 0
    PAD_TYPE_COLUMN = 5
    PAD_DIRECTION_COLUMN = 6
    PAD_POS_X_COLUMN = 1
    PAD_POS_Y_COLUMN = 2
    PAD_SIZE_X_COLUMN = 3
    PAD_SIZE_Y_COLUMN = 4
    NAME_COL_SIZE = 390
    REF_COL_SIZE = 50
    DIR_COL_SIZE = 60

    def __call__(self):
        return self.value
