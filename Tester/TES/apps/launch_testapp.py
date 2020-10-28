"""
utility script to start the testapp as standalone app (without control)
this solely exists to have a counterpart of the launch_master.py and
launch_control.py scripts in integration tests.
"""
import sys


def launch_testapp(argv):
    from ATE.Tester.sequencers.SequencerMqttClient import SequencerMqttClient
    SequencerMqttClient.run_from_command_line(argv)


if __name__ == "__main__":
    launch_testapp(sys.argv)
