from ate_test_app.sequencers.binning.BinStrategy import BinStrategy
from ate_test_app.sequencers.binning.BinStrategyExternal import BinStrategyExternal


def create_bin_strategy(typ, test_program_path: str, test_program_name: str):
    if typ == 'file':
        return BinStrategy(test_program_path)
    if typ == 'external':
        return BinStrategyExternal(test_program_path, test_program_name)

    raise Exception(f"'{typ}' strategy typ is not supported")
