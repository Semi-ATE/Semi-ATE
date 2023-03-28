import os
import sys
from time import sleep
from pathlib import Path
import json
import psutil
import shutil
import subprocess
from semi_ate_testers.testers.tester_interface import TesterInterface
from SCT8.tester import TesterImpl



class MiniSCTSTI:
    """Sub-class, Interface to STI protocol of the MiniSCT, called from :class:`MiniSCT`.

    :Date: |today|
    :Author: "Zlin526F@github"

    Example: Read/Write register

        >>> tester = MiniSCT()
        >>> interface.do_init_state()

        >>> tester.sti.writebase(0)
        >>> tester.sti.writer"/tmp/STIL.hdf5"eg(0x20, 0b1101)
        >>> tester.sti.readreg(0x20)
    """

    def __init__(self, board, logger):
        """Initialise STI interface."""
        self.logger = logger
        self.board = board
        self.tdelay = 0.01

    def __repr__(self):
        args = []
        args.append('{!r}'.format(self.board))
        return '{classname}({args})'.format(
            classname=self.__class__.__name__,
            args=', '.join(args),)

    def init(self):
        self.board.PF.sti_start()

    def readreg(self, addr):
        """Return data in register addr."""
        self.board.protocol_typ = 'sti'
        value = self.board.PF.sti_read(addr)

        if (type(value) == int and value == -1):
            self.board.errortext = value
            self.board.ReadErrorCount += 1
            self.logger.error('{}: {}'.format(self.board.instName, value))
        else:
            self.board.ReadErrorCount = 0
        return value

    def writereg(self, addr, data):
        """Write data to register addr."""
        self.board.protocol_typ = 'sti'
        self.board.PF.sti_write(addr, data)

    def writebase(self, bank):
        """Set register bank."""
        self.board.protocol_typ = 'sti'
        self.board.PF.sti_page(bank)

    def reset(self):
        """Reset from DUT."""
        self.board.protocol_typ = 'sti'
# TODO!  not implemented yet
        self.board.write('stires')
        self.board.ReadErrorCount = 0

    def reset_internal(self):
        """Reset from DUT."""
        self.board.protocol_typ = 'sti'
# TODO!  not implemented yet
        self.board.write('stiresint')
        self.board.ReadErrorCount = 0

    @property
    def delay(self):
        """Set/get delay after each write (default=100ms)."""
        sleep(self.tdelay)
        return (self.tdelay)

    @delay.setter
    def delay(self, value):
        self.tdelay = value


class MiniSCTBiPhase:
    """Sub-class, Interface to BiPhase protocol of the MiniSCT called from :class:`MiniSCT`.

Example: Read/Write register

    >>> tester = MiniSCT()
    >>> tester.do_init_state()

    >>> tester.biph.writebase(0)
    >>> tester.biph.writereg(0x20, 0b1101)
    >>> tester.biph.readreg(0x20)

"""

    def __init__(self, board, logger):
        """Initialise Biphase interface."""
        self.board = board
        self.logger = logger
        self.tdelay = 0.1

# TODO! implement biphase


class MiniSCT(TesterInterface, TesterImpl):
    SITE_COUNT = 1

    def __init__(self, logger=None):
        TesterInterface.__init__(self, logger)
        self._protocol_typ = ''
        self.error = False

    def do_request(self, site_id: int, timeout: int) -> bool:
        '''==> es fehlt eine FUnktion die einmal vor dem eigentlichen start der tests aufgeruffen wird'''
        self.log_info(f'MiniSCT.do_request(site_id={site_id})')
        if not hasattr(self, 'PF'):
            self.turnOn()
            self.sti = MiniSCTSTI(board=self, logger=self.logger)
            self.biph = MiniSCTBiPhase(board=self, logger=self.logger)
            self.interface = self
        return True

    def test_in_progress(self, site_id: int):
        self.log_info(f'MiniSCT.test_in_progress(site_id={site_id})')
        pass

    def test_done(self, site_id: int, timeout: int):
        self.log_info(f'MiniSCT.test_done({site_id})')

    def do_init_state(self, site_id: int):
        TesterImpl.__init__(self)
        self._protocol_typ = 'sti'
        self.log_info(f'MiniSCT.do_init_state(site_id={site_id})')

    def setup(self):
        self.log_info('MiniSCT.setup()')
        pass

    def teardown(self):
        self.log_info('MiniSCT.teardown')
        self.turnOff()

    def run_pattern(self, pattern_name: str, start_label: str = '', stop_label: str = '', timeout: int = 1000):
        self.pf.run(pattern_name, start_label, stop_label, timeout)

    def on(self):
        self.turnOn()

    def off(self):
        self.turnOff()

    @property
    def protocol_typ(self):
        """Set/get protocol typ."""
        return (self._protocol_typ)

    @protocol_typ.setter
    def protocol_typ(self, value):
        if value != self._protocol_typ:
            self._protocol_typ = value
            self.__getattribute__(self._protocol_typ).init()
            self.delay = self.__getattribute__(self._protocol_typ).delay
