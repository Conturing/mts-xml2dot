#!/usr/bin/env python3

import argparse
import json
import logging
import sys
import datetime as dt
from pathlib import Path, PurePath
from pprint import pprint

import yaml

from dot2xml import modal_to_dot
from parse_dot import parse_dot
from parse_xml import parse_xml
from test_case import read_directory


def noattr(args):
    log.error('No command provided!')
    aparser.print_help()
    exit(-1)


def convert(args):
    default_options = {
        'input': '',
        'output': '',
        'mc': False,
        'auto_group': False
    }
    default_options.update(vars(args))

    ipath = Path(default_options['input'])
    opath = Path(default_options['output'])

    pprint(default_options)

    if not ipath.exists():
        log.error(f'Given path does not exists, can not read: {ipath}')
        exit(-1)

    if ipath.suffix not in ['.dot', '.xml']:
        log.error(f'Unknown suffix: {ipath.suffix}')
        exit(-1)
    if opath.suffix not in ['.dot', '.xml']:
        log.error(f'Unknown suffix: {opath.suffix}')
        exit(-1)

    mts_repr = None
    if ipath.suffix == '.dot':
        log.debug(f'Read input (dot): {ipath}')
        mts_repr = parse_dot(ipath)
    elif ipath.suffix == '.xml':
        log.debug(f'Read input (xml): {ipath}')
        mts_repr = parse_xml(ipath)

    if opath.suffix == '.dot':
        log.info(f'Writing to {opath} ...')
        modal_to_dot(path=opath, mts=mts_repr, mc=default_options['mc'], derive_groups=default_options['auto_group'])
    elif opath.suffix == '.xml':
        pass


def create_tests_from_dag(args):
    default_options = {
        'dag': "examples/problem101-decomposition-DAG.dot",
        'output': 'test_cases.json'
    }
    default_options.update(vars(args))

    tests = read_directory(default_options['dag'])

    def normalizePath(path: Path):
        path.resolve()
        return str(path.name)

    norm_tests = {
        'modalCompositionTests': [],
        'modalDecompositionTests': []
    }

    for test_case in tests:
        norm_test_case = dict(test_case)
        for param_type, value in test_case.items():
            if isinstance(value, Path):
                norm_test_case[param_type] = normalizePath(value)
        test_type = test_case['type']
        del norm_test_case['type']
        if test_type == 'comp':
            norm_tests['modalCompositionTests'].append(norm_test_case)
        elif test_type == 'decomp':
            norm_tests['modalDecompositionTests'].append(norm_test_case)

    with open(default_options['output'], 'wt', encoding='utf8') as fileptr:
        json.dump(norm_tests, fileptr, indent=4, sort_keys=True)


# DEFINE COMMANDLINE OPTIONS
aparser = argparse.ArgumentParser(
    prog='Modal contract helper',
    description='Convert modal contracts and modal transitions systems to .dot and .xml'
)
aparser.add_argument('--verbose', required=False, action='store_true', help='Verbose output')
aparser.add_argument('--config', type=str, required=False, help='Define custom path to config file')
aparser.add_argument('--log', type=str, required=False, help='Define log level')
aparser.set_defaults(func=noattr)
subparsers = aparser.add_subparsers()

converter = subparsers.add_parser('convert', aliases=['cv'], help='Convert between dot and xml syntax')
converter.add_argument('-i', '--input', required=True, type=str, help='Input path (format and dialect are automatically deduced)')
converter.add_argument('-o', '--output', required=True, type=str, help='Output path (format is automatically deduced)')
converter.add_argument('--mc', required=False, action='store_true', help='Switch output format to mc-dialect (default is mts)')
converter.add_argument('--auto-group', required=False, action='store_true', help='Derive group numbers automatically (overwriting existing)')
converter.set_defaults(func=convert)

tests = subparsers.add_parser('test', help='Generate test cases out of existing (de)compositions.')
tests.add_argument('--dag', required=True, type=str, help='Generate tests from the given DAG')
tests.add_argument('-o', '--output', required=False, type=str, help='Output tests to given path (format: json)')
tests.set_defaults(func=create_tests_from_dag)
uargs = aparser.parse_args()

# DEFAULT OPTIONS
default_options = {
    'loglevel': 'INFO',
    'logdir': 'log'
}

# LOAD CONFIG FILE
config_path = None
if uargs.config is not None:
    config_path = Path(uargs.config)
else:
    temp_path = Path(__file__).parent.absolute()
    if temp_path.match(r'*.pyz'):
        temp_path = temp_path.parent
    temp_path = Path(temp_path, 'config.yaml')
    if temp_path.exists():
        config_path = temp_path

if config_path is not None:
    try:
        print(f'Loading config file {config_path}')
        config = yaml.safe_load(config_path.open())
    except IOError as e:
        print(f'Error loading config file \'{config_path}\': {e}')
    else:
        default_options.update(config)

# INSTANTIATE LOGGER
levels = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warn': logging.WARNING,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG
}
if uargs.log is not None:
    level = levels.get(uargs.log.lower())
else:
    level = levels.get(default_options['loglevel'].lower())
if level is None:
    raise ValueError(
        f"log level given: {uargs.log if uargs.log is not None else default_options['loglevel']}"
        f" -- must be one of: {' | '.join(levels.keys())}")
logpath = Path(default_options['logdir'], dt.datetime.now().strftime("%Y_%m_%d__%H_%M_%S") + '.log')

handlers = []
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
stdout_handler.setLevel(level)
handlers.append(stdout_handler)
if logpath.parent.exists():
    file_handler = logging.FileHandler(logpath)
    file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    file_handler.setLevel(logging.DEBUG)
    handlers.append(file_handler)
logging.basicConfig(handlers=handlers)
log = logging.getLogger('log')
log.setLevel(logging.DEBUG)


if __name__ == "__main__":
    # create_tests_from_dag()
    print('Modal contract helper')
    uargs.func(uargs)
    print('Done!')
