from ate_test_app.parameters.LocalResolver import LocalResolver
from ate_test_app.sequencers.DutTesting.TestParameters import InputParameter
from ate_test_app.parameters.RemoteResolver import RemoteResolver


def create_parameter_resolver(type, name: str, shmoo: bool, value: object, min_value: float, max_value: float, power: int, context: str):
    # Value contains the actual object to use to resolve the value,
    # or the plain value in case of a static resolver.
    # For remote resolvers the value contains the name of
    # the value that is to be resolved. The type in this case
    # contains  string "remote:" followed by the cache type.
    # -> Now we just need the actual instance.
    if type == 'static':
        return InputParameter(name, shmoo, value, min_value, max_value, power)
    elif type == 'local':
        return LocalResolver(name, shmoo, value, min_value, max_value, power)
    elif 'remote' in type:
        resolvername = type.split(":")[1]
        try:
            plugin_instance = context.gp_dict[resolvername]
            return RemoteResolver(value, plugin_instance)
        except KeyError:
            raise f"The remote resolver {resolvername} is not available in this configuration"
    else:
        raise 'not implemented yet'
