#
import os

standard_tests_directory = os.path.dirname(__file__)
names = {}

def entry_is_a_standard_test(name):
    if name.startswith('__'):
        return False
    if not os.path.isdir(os.path.join(standard_tests_directory, name)):
        return False
    if not os.path.exists(os.path.join(standard_tests_directory, name, '__init__.py')):
        return False
    if not os.path.exists(os.path.join(standard_tests_directory, name, f'{name}.py')):
        return False
    return True

for entry in os.listdir(standard_tests_directory):
    if entry_is_a_standard_test(entry):
        names[entry] = os.path.join(standard_tests_directory, entry, f'{entry}.py')


if __name__ == '__main__':
    for index, name in enumerate(names):
        print(f"{index+1}) {name} : {names[name]}")
