

class RemoteResolver:
    def __init__(self, value_name: str, resolver_plugin_instance: object):
        self._name = value_name
        self.plugin_instance = resolver_plugin_instance

    def __call__(self):
        stdf_record = self.plugin_instance.get_cached_value(self._name)
        if stdf_record is not None:
            return float(stdf_record['RESULT'])
        # TBD: What should we do if it turns out, the value is not available
        #      in the cache (e.g. due to a test being not completed)
