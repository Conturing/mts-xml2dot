import os
import pprint
import re
from os import PathLike
from pathlib import Path
from typing import Mapping, Sequence, Tuple, Union

import networkx as nx
import networkx.algorithms.isomorphism as iso
import matplotlib.pyplot as plt
import pygraphviz as pgv

from export_dot import modal_to_dot
from parse_dot import parse_dot
import logging

from parse_xml import parse_xml

log = logging.getLogger(__name__)
log.setLevel(level=logging.DEBUG)

modal_contracts = []


def read_directory(path_to_dag) -> Sequence[Mapping[str, PathLike]]:
    path_to_dag = Path(path_to_dag)
    path_to_dag.resolve()
    dag = nx.drawing.nx_pydot.read_dot(path_to_dag)

    roots = [n for n, d in dag.in_degree() if d == 0]
    log.info(f'Found {len(roots)} root components')

    base_dir = path_to_dag.parent

    for file in os.scandir(base_dir):
        if file.is_file() and re.match(r'.*-mc-.*\.xml', file.name):
            mc_path = convert_component(Path(base_dir, file.name), mc=True)
            mc_graph = nx.drawing.nx_pydot.read_dot(mc_path)
            modal_contracts.append((mc_graph, mc_path))

    tests = []
    for root in roots:
        test_case, _ = add_branch(dag, root, Path(path_to_dag.parent))
        tests += test_case

    return tests


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

        log.info('Finding corresponding modal-contract ...')

        log.debug(f'mc subgraph search for {rename}')
        current_subgraph = nx.drawing.nx_pydot.read_dot(rename)

        def is_subgraph(mc_info) -> bool:
            nonlocal current_subgraph
            graph, path = mc_info
            try:
                GM = iso.GraphMatcher(graph, current_subgraph, edge_match=iso.categorical_edge_match(['label'], ['-']))
                return GM.subgraph_is_monomorphic()
            except KeyError:
                log.debug('Lib-Error in subgraph matching!')
                return False

        candidates = list(filter(is_subgraph, modal_contracts))
        if len(candidates) > 1:
            log.info(f'Found multiple matching contracts: {candidates}')
        elif len(candidates) == 0:
            log.warning('Found no matching contract!')
        else:
            test['modal_contract'] = candidates[0][1]
            modal_contracts.remove(candidates[0])

        #best_fit = max(modal_contracts, key=lambda mc: nx.graph_edit_distance(current_subgraph, mc))
        #modal_contracts.remove(best_fit)
        #print(nx.graph_edit_distance(current_subgraph, best_fit))

        test['orig_sys'] = rename

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
        pass
        #return rename_to

    graph_repr = parse_xml(root_file)
    modal_to_dot(str(rename_to.absolute()), graph_repr, mc=mc)

    return rename_to

