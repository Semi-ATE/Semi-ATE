
from math import inf, nan
import common
import sys
import os
from ate_test_app.sequencers.SequencerBase import SequencerBase
from ate_test_app.sequencers.CommandLineParser import CommandLineParser
from ate_test_app.sequencers.binning.BinStrategyFactory import create_bin_strategy
from ate_common.logger import Logger


if __name__ == '__main__':
    # Start MQTT using the sequencer.
    # Note that run_from_command_line_with_sequencer will
    # only return when the program should terminate.
    params = CommandLineParser(sys.argv)
    test_program_name, _ = os.path.splitext(__file__)
    bin_table_name = f'{test_program_name}_binning.json'
    bin_table_path = os.path.join(os.path.dirname(__file__), bin_table_name)
    bin_strategy = create_bin_strategy(params.strategytype, bin_table_path, test_program_name)

    program_name = os.path.basename(__file__).replace(".py", "")
    sequencer = SequencerBase(program_name, bin_strategy)

    from project_version_3_HW0_FT_a_maintenance_lazyme_auto_script import AutoScript
    auto_script = AutoScript()
    source = f"TestApp{params.site_id}"
    context = common.make_context(source, params, sequencer, auto_script)

    logger = context.get_logger()
    sequencer.set_logger(logger)
    auto_script.set_logger(logger)
    auto_script.set_context(context)

    sequencer.set_auto_script(auto_script)

    from iddq.iddq import iddq
    _ate_var_iddq_1 = iddq("iddq_1", context)
    _ate_var_iddq_1.set_sbin(60000)
    _ate_var_iddq_1.set_test_num(100)

    _ate_var_iddq_1.ip.set_parameter('Temperature', 'static', 25, -40.0, 170.0, 0, context)

    _ate_var_iddq_1.op.set_parameter('new_parameter1', 101, nan, nan, 11, 2, 'iddq_1')

    sequencer.register_test(_ate_var_iddq_1)

    sequencer.set_tester_instance(context.tester_instance)


    context.mqtt.set_logger(logger)
    context.mqtt.run_from_command_line_with_sequencer()
    logger.cleanup()
