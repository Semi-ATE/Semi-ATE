import common
import sys
import os
from numpy import nan, inf
from ATE.Tester.TES.apps.testApp.sequencers.SequencerBase import SequencerBase
from ATE.Tester.TES.apps.testApp.sequencers.CommandLineParser import CommandLineParser
from ATE.Tester.TES.apps.testApp.sequencers.binning.BinStrategyFactory import create_bin_strategy
from ATE.common.logger import Logger


if __name__ == '__main__':
    # Start MQTT using the sequencer.
    # Note that run_from_command_line_with_sequencer will
    # only return when the program should terminate.
    params = CommandLineParser(sys.argv)
    test_program_name, _ = os.path.splitext(__file__)
    bin_table_name = f'{test_program_name}_binning.json'
    bin_table_path = os.path.join(os.path.dirname(__file__), bin_table_name)
    bin_strategy = create_bin_strategy(params.binstrategytype, bin_table_path, test_program_name)

    program_name = os.path.basename(__file__).replace(".py", "")
    sequencer = SequencerBase(program_name, bin_strategy)

    source = f"TestApp{params.site_id}"
    context = common.make_context(source, params, sequencer)

    logger = context.get_logger()
    sequencer.set_logger(logger)

    from iddq.iddq import iddq
    _ate_var_iddq_1 = iddq(context)
    _ate_var_iddq_1.set_sbin(60000)
    _ate_var_iddq_1.set_test_num(100)

    _ate_var_iddq_1.ip.set_parameter('Temperature', 'static', 25, -40.0, 170.0, 0, context)

    _ate_var_iddq_1.op.set_parameter('new_parameter1', 101, nan, nan, 11, 2, 'iddq_1')

    sequencer.register_test(_ate_var_iddq_1)
    from iddq.iddq import iddq
    _ate_var_iddq_2 = iddq(context)
    _ate_var_iddq_2.set_sbin(60001)
    _ate_var_iddq_2.set_test_num(200)

    _ate_var_iddq_2.ip.set_parameter('Temperature', 'static', 25, -40.0, 170.0, 0, context)

    _ate_var_iddq_2.op.set_parameter('new_parameter1', 201, nan, nan, 11, 2, 'iddq_2')

    sequencer.register_test(_ate_var_iddq_2)

    sequencer.set_tester_instance(context.tester_instance)


    context.mqtt.set_logger(logger)
    context.mqtt.run_from_command_line_with_sequencer()
    logger.cleanup()
