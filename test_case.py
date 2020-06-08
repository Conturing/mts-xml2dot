import pprint
import re
from os import PathLike
from pathlib import Path
from typing import Mapping, Sequence, Tuple, Union

import networkx as nx

from dot2xml import mts_to_dot, mc_to_dot
from parse_dot import parse_dot
import logging

from parse_xml import parse_xml

log = logging.getLogger(__name__)
log.setLevel(level=logging.INFO)


def read_directory(path_to_dag):
    path_to_dag = Path(path_to_dag)
    path_to_dag.resolve()
    dag = nx.drawing.nx_pydot.read_dot(path_to_dag)

    roots = [n for n, d in dag.in_degree() if d == 0]
    log.info(f'Found {len(roots)} root components')

    for root in roots:
        pprint.pprint(add_branch(dag, root, Path(path_to_dag.parent)))


def add_branch(graph: nx.DiGraph, root_node, base_path) -> Tuple[Sequence[Mapping], Path]:
    rename = convert_component(Path(base_path, root_node))
    test_cases = []
    test = {}

    out_degree = graph.out_degree(root_node)
    in_degree = graph.in_degree(root_node)

    if out_degree == 2:
        log.info('Found decomposition')
        test['type'] = 'decomp'

        for child in graph.adj[root_node]:
            if re.match(r'.*extended.*context.*', child):
                log.warning(f'Found extended context. Trying to find base context ...')
                context = Path(base_path, re.sub('extended-', '', child))
                if not context.exists():
                    log.error('Can not find context!')
                    raise FileNotFoundError(f'Context component not found, expected \'{context}\'')
                new_context = convert_component(context)
                test['context'] = new_context
            elif re.match(r'.*system.*', child):
                child_path = convert_component(Path(base_path, child))
                test['system'] = child_path

        test['orig_sys'] = rename
        test_cases.append(test)

    elif in_degree == 2:
        log.info('Found composition')
        test['type'] = 'comp'

        id = 0
        for child in graph.predecessors(root_node):
            child_path = convert_component(Path(base_path, child))
            test[f'input{id}'] = child_path
            id += 1

        test['merge'] = rename

    else:
        log.warning(f'Found passing node {root_node}')

    if len(test) > 0:
        test_cases.append(test)

    for child in graph.adj[root_node]:
        tests, _ = add_branch(graph, child, base_path)
        test_cases += tests

    return test_cases, rename


def convert_component(path: Union[str, PathLike], mc=False) -> Path:
    root_file = Path(path)
    if not root_file.exists():
        raise FileNotFoundError(f'File does not exists: {root_file}')
    elif root_file.suffix != '.xml':
        raise ValueError(f'Expected xml file, got {root_file.suffix}')

    rename_to = root_file.with_suffix('.dot')
    if rename_to.exists():
        return rename_to

    graph_repr = parse_xml(root_file)
    modal_to_dot(str(rename_to.absolute()), graph_repr, mc=mc)

    return rename_to

