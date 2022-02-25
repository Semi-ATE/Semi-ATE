from multiprocessing.dummy import Process
from helpers import create_setup, create_structure
from pathlib import Path


version = '1.0.0'
target_url = './temp'

# packages

# In case of the spyder package it is important to name it Semi-ATE as spyder seems to
# check whether a plugin named Semi-ATE can befound, if not spyder will show some popup
# claiming that a dependency coould not be found
spyder_plugin = {
    'description' : 'Spyder ate plugin for working with ATE projects',
    'entry_points' : '''"spyder.plugins": ["ate = ATE.spyder.plugin:ATE"]''',
    'name' : 'Semi-ATE',
    'prefix_url' : 'ATE/spyder',
    'source_url' : '../ATE/spyder',
}

common = {
    'description' : 'Common package of ATE Projects',
    'name' : 'ate-common',
    'entry_points' : None,
    'prefix_url' : 'ATE/common',
    'source_url' : '../ATE/common',
}

project_database = {
    'description' : 'Projectdatabase of ATE Test Projects',
    'name' : 'ate-projectdatabase',
    'entry_points' : None,
    'prefix_url' : 'ATE/projectdatabase',
    'source_url' : '../ATE/projectdatabase',
}

semi_ate_plugin = {
    'description' : 'SemiATE plugin for Projectdatabase of ATE Test Projects',
    'name' : 'semi-ate-plugins',
    'entry_points' : None,
    'prefix_url' : 'ATE/semiateplugins',
    'source_url' : '../ATE/semiateplugins',
}

packages = [
    spyder_plugin,
    common,
    project_database,
    semi_ate_plugin,
]

# generate packages
for p in packages:
    print(f'Generating package {p["name"]} in folder: {target_url}')
    create_structure(p['name'], p['prefix_url'], p['source_url'], target_url)
    create_setup(str(Path(target_url, p['name'])), version, p['name'], p['description'], p['entry_points'])

# generate packages

