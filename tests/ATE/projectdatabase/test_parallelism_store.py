from pytest import fixture

from ATE.projectdatabase.Hardware.ParallelismConfig import ParallelismConfig
from ATE.projectdatabase.Hardware.ParallelismStore import ParallelismStore
from ATE.projectdatabase.Utils import BaseType


@fixture
def mock_config_tables_without_coordinates():
    return [
        ParallelismConfig.new("PR1A", BaseType.PR, 1),
        ParallelismConfig.new("PR5A", BaseType.PR, 5),
        ParallelismConfig.new("PR16A", BaseType.PR, 16),
        ParallelismConfig.new("FT1A", BaseType.FT, 1),
        ParallelismConfig.new("FT5A", BaseType.FT, 5),
        ParallelismConfig.new("FT16A", BaseType.FT, 16)
    ]


@fixture
def config_store():
    return ParallelismStore()


@fixture
def tables_data():
    DUMMY_TABLE_DATA = [
        [
            ParallelismConfig.new("PR4A", BaseType.PR, 4),
            {1: (1, 0), 2: (0, 1), 3: (0, 2), 4: (3, 0)},
            [
                ("sequence", [{0, 1, 2, 3}]),
                ("even_odd", [{0, 2}, {1, 3}])
            ]
        ],
        [
            ParallelismConfig.new("PR3A", BaseType.PR, 3),
            {1: (0, 0), 2: (0, 1), 3: (0, 2)},
            [
                ("sequence", [{0, 1, 2}])
            ]
        ],
        [
            ParallelismConfig.new("PR3B", BaseType.PR, 3),
            {1: (0, 0), 2: (0, 1), 3: (0, 2)},
            [
                ("sequence", [{0, 1, 2}])
            ]
        ],
        [
            ParallelismConfig.new("PR3C", BaseType.PR, 3),
            {1: (0, 0), 2: (0, 1), 3: (0, 3)},
            [
                ("sequence", [{0, 1, 2}])
            ]
        ],
        [
            ParallelismConfig.new("FT3A", BaseType.FT, 3),
            {1: (0, 0), 2: (0, 1), 3: (0, 3)},
            [
                ("sequence", [{0, 1, 2}])
            ]
        ]
    ]
    tables = []
    for table in DUMMY_TABLE_DATA:
        new_table = table[0]
        new_table.cells = table[1]
        for ping_pong in table[2]:
            new_table.add_ping_pong_config(ping_pong[0], len(ping_pong[1]))
            for index, stage in enumerate(ping_pong[1]):
                # Inject stage data into generated PingPongStage class
                new_table.configs[-1].stages[index].stage = stage
        tables.append(new_table)
    return tables


@fixture
def tables_data_serialized():
    return {
        'PR': [
            {
                'next_ping_pong_id': 3,
                'name': 'PR4A',
                'sites': [(1, 0), (0, 1), (0, 2), (3, 0)],
                'configs': [
                    {'id': 0, 'name': 'All Parallel', 'stages': [['0', '1', '2', '3']]},
                    {'id': 1, 'name': 'sequence', 'stages': [['0', '1', '2', '3']]},
                    {'id': 2, 'name': 'even_odd', 'stages': [['0', '2'], ['1', '3']]}
                ]
            },
            {
                'next_ping_pong_id': 2,
                'name': 'PR3A',
                'sites': [(0, 0), (0, 1), (0, 2)],
                'configs': [
                    {'id': 0, 'name': 'All Parallel', 'stages': [['0', '1', '2']]},
                    {'id': 1, 'name': 'sequence', 'stages': [['0', '1', '2']]}
                ]
            },
            {
                'next_ping_pong_id': 2,
                'name': 'PR3B',
                'sites': [(0, 0), (0, 1), (0, 2)],
                'configs': [
                    {'id': 0, 'name': 'All Parallel', 'stages': [['0', '1', '2']]},
                    {'id': 1, 'name': 'sequence', 'stages': [['0', '1', '2']]}]},
            {
                'next_ping_pong_id': 2,
                'name': 'PR3C',
                'sites': [(0, 0), (0, 1), (0, 3)],
                'configs': [
                    {'id': 0, 'name': 'All Parallel', 'stages': [['0', '1', '2']]},
                    {'id': 1, 'name': 'sequence', 'stages': [['0', '1', '2']]}
                ]
            }
        ],
        'FT': [
            {
                'next_ping_pong_id': 2,
                'name': 'FT3A',
                'sites': [(0, 0), (0, 1), (0, 3)],
                'configs': [
                    {'id': 0, 'name': 'All Parallel', 'stages': [['0', '1', '2']]},
                    {'id': 1, 'name': 'sequence', 'stages': [['0', '1', '2']]}
                ]
            }
        ]
    }


def test_gen_suffix():
    assert ParallelismStore.gen_suffix(0) == 'A'
    assert ParallelismStore.gen_suffix(26) == 'AA'
    assert ParallelismStore.gen_suffix(52) == 'BA'


def test_generate_next_config_name(config_store, mock_config_tables_without_coordinates):
    assert config_store.generate_next_config_name(BaseType.PR, 1) == "PR1A"
    assert config_store.generate_next_config_name(BaseType.PR, 16) == "PR16A"
    assert config_store.generate_next_config_name(BaseType.FT, 1) == "FT1A"
    for dummy in mock_config_tables_without_coordinates:
        config_store.add(dummy)
    assert config_store.generate_next_config_name(BaseType.PR, 1) == "PR1B"
    assert config_store.generate_next_config_name(BaseType.PR, 16) == "PR16B"
    assert config_store.generate_next_config_name(BaseType.FT, 1) == "FT1B"


def test_does_pattern_match_different_site_count(tables_data):
    assert not ParallelismStore.does_pattern_match(tables_data[0], tables_data[1])


def test_does_pattern_match_true(tables_data):
    assert ParallelismStore.does_pattern_match(tables_data[1], tables_data[2])


def test_does_pattern_match_different_coordinates(tables_data):
    assert not ParallelismStore.does_pattern_match(tables_data[2], tables_data[3])


def test_does_pattern_match_different_pattern_type(tables_data):
    assert not ParallelismStore.does_pattern_match(tables_data[3], tables_data[4])


def test_min_required_parallelism(config_store, mock_config_tables_without_coordinates):
    config_store.add_all(mock_config_tables_without_coordinates)
    assert config_store.min_required_parallelism() == 16


def test_find_duplicate(config_store, tables_data):
    config_store.add_all(tables_data)
    flag, a, b = config_store.find_duplicate()
    assert flag
    assert a is not None
    assert b is not None
    config_store.remove("PR3A")
    flag, a, b = config_store.find_duplicate()
    assert not flag
    assert a is None
    assert b is None


def test_all_tables_filled(config_store, tables_data):
    config_store.add_all(tables_data)
    assert config_store.all_tables_filled()


def test_all_tables_filled_no(config_store, tables_data, mock_config_tables_without_coordinates):
    config_store.add_all(tables_data)
    config_store.add_all(mock_config_tables_without_coordinates)
    assert not config_store.all_tables_filled()


def test_serialize(config_store, tables_data, tables_data_serialized):
    config_store.add_all(tables_data)
    assert config_store.serialize() == tables_data_serialized


def test_from_database(config_store, tables_data, tables_data_serialized):
    config_store = config_store.from_database(tables_data_serialized)
    for table in tables_data:
        assert table.name in config_store.parallelism_store


def test_are_all_configs_correct_default(config_store, tables_data):
    config_store.add_all(tables_data)
    for name, parallelism in config_store.get_all().items():
        ok, msg = parallelism.are_all_configs_correct()
        assert ok, msg


def test_are_all_configs_correct_missing_site(config_store, tables_data):
    config_store.add_all(tables_data)
    for name, parallelism in config_store.get_all().items():
        for ping_pong in parallelism.configs:
            ping_pong.stages[0].stage.pop()
        ok, msg = parallelism.are_all_configs_correct()
        assert not ok


def test_are_all_configs_correct_duplicate_sites(config_store, tables_data):
    config_store.add_all(tables_data)
    for name, parallelism in config_store.get_all().items():
        modified = False
        for ping_pong in parallelism.configs:
            if len(ping_pong.stages) >= 2:
                ping_pong.stages[0].stage.update(ping_pong.stages[1].stage)
                modified = True
        if modified:
            ok, msg = parallelism.are_all_configs_correct()
            assert not ok


def test_are_all_configs_correct_empty_stage(config_store, tables_data):
    config_store.add_all(tables_data)
    for name, parallelism in config_store.get_all().items():
        parallelism.configs[0].stages[0].stage.clear()
        ok, msg = parallelism.are_all_configs_correct()
        assert not ok
