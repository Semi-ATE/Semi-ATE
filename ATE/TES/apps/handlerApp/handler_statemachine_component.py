from enum import Enum


class States(Enum):
    idle = "idle"
    prepareLotTest = "prepareLotTest"
    loadingLotTest = "loadingLotTest"
    ready = "ready"
    testing = "testing"
    binning = "binning"
    indexing = "indexing"
    unloadLotTest = "unloadLotTest"

    @classmethod
    def list(cls):
        return [x.value for x in list(cls)]

    def __str__(self):
        return f'{self.value}'


class Transitions(Enum):
    trans1 = {'source': States.idle, 'dest': States.prepareLotTest, 'trigger': 'new_lot'}
    trans2 = {'source': States.prepareLotTest, 'dest': States.loadingLotTest, 'trigger': 'data_ready'}
    trans3 = {'source': States.loadingLotTest, 'dest': States.ready, 'trigger': 'master_ready'}
    trans4 = {'source': States.ready, 'dest': States.testing, 'trigger': 'send_start_cmd'}
    trans5 = {'source': States.testing, 'dest': States.binning, 'trigger': 'test_result_received'}
    trans6 = {'source': States.binning, 'dest': States.indexing, 'trigger': 'binning_success'}
    trans7 = {'source': States.indexing, 'dest': States.ready, 'trigger': 'indexing_complete_master_ready'}
    trans8 = {'source': States.indexing, 'dest': States.unloadLotTest, 'trigger': 'lot_end'}
    trans9 = {'source': States.unloadLotTest, 'dest': States.idle, 'trigger': 'master_initialized'}
    # TODO: error states

    @classmethod
    def list(cls):
        return [x.value for x in list(cls)]
