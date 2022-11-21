
"""
Creating a singleton in Python

see https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
"""


def singleton(cls):
    """
Create Singleton by decorator

Pros

    Decorators are additive in a way that is often more intuitive than multiple
    inheritance.

Cons

    While objects created using MyClass() would be true singleton objects, MyClass
    itself is a a function, not a class, so you cannot call class methods from it.
    Also for m = MyClass(); n = MyClass(); o = type(n)(); then m == n && m != o && n != o
    """

    instance = [None]

    def wrapper(*args, **kwargs):
        if instance[0] is None:
            instance[0] = cls(*args, **kwargs)
        return instance[0]
    return wrapper

#
#   @singleton
#   class MyClass(BaseClass):
#      pass
#


class Singleton(type):

    """
Create Singleton by inheriting from a metaclass

Pros

    It's a true class
    Auto-magically covers inheritance
    Uses __metaclass__ for its proper purpose (and made me aware of it)

Cons

    Are there any?
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


#
#  class MyClass(BaseClass, metaclass=Singleton):
#      pass
#
