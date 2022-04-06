from ate_test_app.sequencers.MqttClient import MqttClient
import logging
from transitions import Machine
from ate_test_app.sequencers.TheTestAppStatusAlive import TheTestAppStatusAlive

logger = logging.getLogger(__name__)


class TheTestAppMachine:

    def __init__(self, mqtt: MqttClient):
        self._mqtt = mqtt

        states = ['starting', 'idle', 'testing', 'selftesting', 'terminated', 'error']

        transitions = [
            {'trigger': 'startup_done', 'source': 'starting', 'dest': 'idle', 'before': 'on_startup_done'},
            {'trigger': 'cmd_init', 'source': 'idle', 'dest': 'selftesting', 'before': 'on_cmd_init'},
            {'trigger': 'cmd_next', 'source': 'idle', 'dest': 'testing', 'before': 'on_cmd_next'},
            {'trigger': 'cmd_terminate', 'source': 'idle', 'dest': 'terminated', 'before': 'on_cmd_terminate'},
            {'trigger': 'cmd_done', 'source': ['testing', 'selftesting'], 'dest': 'idle', 'before': 'on_cmd_done'},
            {'trigger': 'fail', 'source': '*', 'dest': 'error', 'before': 'on_fail'},
        ]

        self.machine = Machine(model=self, states=states, transitions=transitions, initial='starting', after_state_change=self.after_state_change)

    def after_state_change(self, whatever=None):
        logger.debug('publish_current_state: %s', self.state)

        if self.is_error() or self.is_terminated():
            dodisconnect = True
            alive = TheTestAppStatusAlive.DEAD
        else:
            dodisconnect = False
            alive = TheTestAppStatusAlive.ALIVE

        msginfo = self._mqtt.publish_status(alive, {'state': self.state, 'payload': {'state': self.state, 'message': ''}})
        msginfo.wait_for_publish()

        # workaround: handle state after publishing status (which is done
        # in after_state_change, so we cannot put this logic into
        # before/after_transition or on_state handler)
        if dodisconnect:
            self._mqtt.disconnect()

    def on_startup_done(self):
        logger.debug('on_startup_done')

    def on_cmd_init(self):
        logger.debug('on_cmd_init')

    def on_cmd_next(self):
        logger.debug('on_cmd_next')

    def on_cmd_terminate(self):
        logger.debug('on_cmd_terminate')

    def on_cmd_done(self):
        logger.debug('on_cmd_done')

    def on_fail(self, info):
        logger.error('on_fail: %s', info)
