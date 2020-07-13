from ATE.org.plugins.hookspec import ATEPlugin

import pluggy


def get_plugin_manager():
    plugin_manager = pluggy.PluginManager("ate.org")
    plugin_manager.add_hookspecs(ATEPlugin)
    plugin_manager.load_setuptools_entrypoints("ate.org")
    return plugin_manager
