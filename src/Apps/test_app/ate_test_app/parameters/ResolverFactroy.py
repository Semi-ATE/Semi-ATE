from ate_test_app.parameters.LocalResolver import LocalResolver
from ate_test_app.sequencers.DutTesting.TestParameters import InputParameter


def create_parameter_resolver(type: str, name: str, shmoo: bool, value: object):
    if type == 'static':
        return InputParameter(name, shmoo, value)
    elif type == 'local':
        return LocalResolver(name, shmoo, value)
    else:
        raise 'not implemented yet'
