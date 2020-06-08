import json
import logging
import sys
import datetime as dt
from pathlib import Path, PurePath

import yaml

from dot2xml import modal_to_dot
from parse_dot import parse_dot
from parse_xml import parse_xml
from test_case import read_directory

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
stdout_handler.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(f'log/{dt.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")}.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
file_handler.setLevel(logging.DEBUG)
logging.basicConfig(handlers=[stdout_handler, file_handler])
log = logging.getLogger('log')


def create_tests_from_dag(path: str = "examples/problem101-decomposition-DAG.dot", output_file: str = 'test_cases.json'):
    tests = read_directory(path)

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

    with open(output_file, 'wt', encoding='utf8') as fileptr:
        json.dump(norm_tests, fileptr, indent=4, sort_keys=True)


if __name__ == "__main__":
    create_tests_from_dag()
