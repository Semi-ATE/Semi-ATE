from ATE.Tester.TES.apps.testApp.sequencers.binning.BinStrategy import BinStrategy


def create_bin_strategy(typ, bin_settings, config_file=None):
    if typ == 'file':
        return BinStrategy(bin_settings, config_file)

    raise Exception(f"'{typ}' strategy typ is not supported")
