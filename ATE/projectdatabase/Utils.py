from enum import Enum


class BaseType(Enum):
    PR = 'PR'
    FT = 'FT'


class DB_KEYS:
    class HARDWARE:
        @staticmethod
        def KEY() -> str:
            return "hardware"
        NAME = "name"
        IS_ENABLED = "is_enabled"

        class DEFINITION:
            @staticmethod
            def KEY() -> str:
                return "definition"
            TESTER = 'tester'

            class PCB:
                @staticmethod
                def KEY() -> str:
                    return "PCB"
                SINGLE_SITE_LOADBOARD = "SingleSiteLoadboard"
                SINGLE_SITE_DIB = "SingleSiteDIB"
                SINGLE_SITE_DIB_IS_CABLE = "SingleSiteDIBisCable"
                SINGLE_SITE_PROBE_CARD = "SingleSiteProbeCard"
                MULTI_SITE_LOADBOARD = "MultiSiteLoadboard"
                MULTI_SITE_DIB = "MultiSiteDIB"
                MULTI_SITE_DIB_IS_CABLE = "MultiSiteDIBisCable"
                MULTI_SITE_CARD = "MultiSiteProbeCard"
                MAX_PARALLELISM = "MaxParallelism"

            class PARALLELISM:
                @staticmethod
                def KEY() -> str:
                    return "Parallelism"
                NAME = "name"
                SITES = "sites"
                NEXT_PING_PONG_ID = "next_ping_pong_id"

                class CONFIGS:
                    @staticmethod
                    def KEY() -> str:
                        return "configs"
                    ID = "id"
                    NAME = "name"
                    STAGES = "stages"

            class ACTUATOR:
                @staticmethod
                def KEY() -> str:
                    return 'Actuator'
                PR = BaseType.PR.value
                FT = BaseType.FT.value

            class INSTRUMENTS:
                @staticmethod
                def KEY() -> str:
                    return "Instruments"

            class GP_FUNCTIONS:
                @staticmethod
                def KEY() -> str:
                    return 'GPFunctions'

    class SEQUENCE:
        OWNER_NAME = 'owner_name'
        PROG_NAME = 'prog_name'
        TEST_NAME = 'test'
        TEST_ORDER = 'test_order'

        class DEFINITION:
            @staticmethod
            def KEY():
                return 'definition'
            IS_SELECTED = "is_selected"
            DESCRIPTION = "description"
            NAME = "name"
            SBIN = "sbin"
            TEST_NUM = "test_num"
            EXECUTIONS = "executions"

            class INPUT_PARAMETERS:
                @staticmethod
                def KEY():
                    return "input_parameters"

                class TEMPERATURE:
                    @staticmethod
                    def KEY():
                        return "Temperature"
                    VALUE = "value"
                    TYPE = "type"
                    MIN = "Min"
                    MAX = "Max"
                    FMT = "fmt"
                    UNIT = "Unit"
                    EXPONENT = "10\u1d61"
                    DEFAULT = "Default"
                    CONTENT = "content"

            class OUTPUT_PARAMETERS:
                @staticmethod
                def KEY():
                    return "output_parameters"
                UTL = "UTL"
                LTL = "LTL"
                LSL = "LSL"
                USL = "USL"
                FMT = "fmt"
                UNIT = "Unit"
                EXPONENT = "10\u1d61"
                TEST_NUM = "test_num"

                class BINNING:
                    @staticmethod
                    def KEY():
                        return "Binning"
                    BIN = "bin"
                    RESULT = "result"
                    NAME = "name"
                    GROUP = "group"
                    DESCRIPTIO = "description"
