from enum import Enum


class Types(Enum):
    Maskset = 'masksets'
    Package = 'package'
    Device = 'device'
    Die = 'die'
    Hardware = 'hardware'
    Product = 'product'
    Program = 'program'
    Qualification = 'qualification'
    Sequence = 'sequence'
    Test = 'test'
    Testtarget = 'testtarget'

    def __call__(self):
        return self.value
