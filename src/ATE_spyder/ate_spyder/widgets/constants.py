"""
Semi-ATE constants.
"""

# Standard library imports
from enum import Enum, IntEnum

# Third-party imports
from spyder.api.translations import get_translation

# Localization
_ = get_translation('spyder')


class TableIds(Enum):
    Flow = 1
    Definition = 2
    Hardware = 3
    Maskset = 4
    Device = 5
    Product = 6
    Package = 7
    Die = 8
    Test = 9
    Program = 10
    TestItem = 11
    NewTest = 12
    RemoveTest = 13

    def __call__(self):
        return self.value


class TranslatedEnumMeta(type):
    def __new__(mcls, name, bases, attrs, **kwargs):
        new_attrs = {}
        translations = {}
        inverse_translations = {}
        for attr in attrs:
            value = attrs[attr]
            if not attr.startswith('_') and isinstance(value, tuple):
                enum_value, translation = value
                translations[enum_value] = translation
                inverse_translations[translation] = enum_value
                value = enum_value
            new_attrs[attr] = value
        new_attrs['translations'] = translations
        new_attrs['inverse_translations'] = inverse_translations

        def get_translation(member):
            return translations[member]

        def get_inverse_translation(translation):
            return inverse_translations[translation]

        new_attrs['get_translation'] = staticmethod(get_translation)
        new_attrs['get_inverse_translation'] = staticmethod(
            get_inverse_translation)
        return super(TranslatedEnumMeta, mcls).__new__(
            mcls, name, bases, new_attrs)

    def __getitem__(cls, value):
        if value in cls.translations:
            return cls.get_translation(value)
        elif value in cls.inverse_translations:
            return cls.get_inverse_translation(value)
        else:
            raise ValueError(f'No entry member or translation was found for '
                             f'{value} in {cls.__qualname__}')


class QualityGrades(metaclass=TranslatedEnumMeta):
    Commercial = ('commercial', _('Commercial'))
    Industrial = ('industrial', _('Industrial'))
    Automotive = ('automotive', _('Automotive'))
    Medical = ('medical', _('Medical'))
    Military = ('military', _('Military'))


class UpdateOptions(IntEnum):
    DB_Update = 0
    Group_Update = 1
    Code_Update = 2

    def __call__(self):
        return self.value


class ATEActions:
    RunStil = 'run_stil'


class ATEToolbars:
    ATE = 'ate_toolbar'


class ATEStatusBars:
    ATE = 'ate_statusbar'


TEST_SECTION = 'tests'
QUALIFICATION = 'qualification'

FLOWS = ['checker', 'maintenance', 'production', 'engineering', 'validation', 'quality', 'qualification']
SUBFLOWS_QUALIFICATION = ['ZHM', 'ABSMAX', 'EC', 'HTOL', 'HTSL', 'DR', 'AC', 'HAST', 'ELFR', 'LU', 'TC', 'THB', 'ESD', 'RSJ']