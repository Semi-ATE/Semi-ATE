# -*- coding: utf-8 -*-


class parameter(object):

    def __init__(self):
        pass

    # This method shall create the ui controls that
    # represent this parameter
    def create_ui_components(self, parent_container, on_change_handler):
        pass

    # The validate method shall yield true, if the
    # data entered in the parameters fields is correct
    def validate(self) -> bool:
        pass

    def _validate_impl(self) -> bool:
        print("base")
        return False

    # Note on de/serialisation of parameters: The first ideas intended to just
    # pickle the whole object tree here, however this has the drawback, that
    # the code of a given object is stored as well, leading to a lot of potential
    # problems down the road, most notably:
    #  * A changed interface of an object will cause issues with pickled instances,
    #    as they don't have these changes
    #  * Changed behavior (e.g. bug fixes) are not promoted into pickled instances,
    #    so we might end up with each pickled instance behaving slightly different.

    # To avoid these issues all parameters are able to write and read their contents
    # to a dict, which can be easily de/serialized (or indeed pickled).
    # The policy for missing data is, to fill up with defined default values.

    # Store values shall put all relevant values for this parameter into the
    # provided dictionary in key-value fashion, where key is the name of the
    # parameter and the value is a tuple of associated parameter values. In
    # the simples case this might boil down to a simple value as well
    # (e.g. in case of an int parameter)
    def store_values(self, dst: dict):
        pass

    # Load value shall attempt to restore the internal state of the parameter
    # based on the contents of a provided dictionary. It shall read data from
    # a dictionary entry whose key corresponds to the parameter's name. The
    # datastructure itself is parameter dependant, and might range from a plain
    # value to a complex tuple. Note, that the parameter shall fallback to
    # default values, if the provided dictionary does not contain all required
    # values.
    def load_values(self, src: dict):
        pass
