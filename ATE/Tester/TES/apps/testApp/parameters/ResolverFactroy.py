from ATE.Tester.TES.apps.testApp.parameters.LocalResolver import LocalResolver
from ATE.Tester.TES.apps.testApp.sequencers.DutTesting.TestParameters import InputParameter


def create_parameter_resolver(type, name, shmoo, value):
    if type == 'static':
        return InputParameter(name, shmoo, value)
    elif type == 'local':
        return LocalResolver(name, shmoo, value)
    else:
        raise 'not implemented yet'
