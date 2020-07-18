from distutils.util import strtobool
from typing import Mapping
from xml.etree import ElementTree as ET
import logging

from mts import MTS

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def parse_xml(path) -> MTS:
    tree = ET.parse(path)
    root = tree.getroot()

    mts = MTS()

    states = root.find('states')
    transitions = root.find('transitions')

    for state in states:
        if state.tag != 'state':
            raise ValueError('Expected tag \'state\'')
        id = state.find('id').text
        for attr in state.find('attributes'):
            if attr.tag != 'isInitial':
                log.warning(f'Tag \'{attr.tag}\' is unknown')
            else:
                initial = bool(strtobool(attr.text))
        mts.add_state(id=id, initial=initial)

    for transition in transitions:
        if transition.tag != 'transition':
            raise ValueError('Expected tag \'transition\'')
        src   = transition.find('sourceId').text
        dest  = transition.find('targetId').text
        label = transition.find('label').text
        try:
            attr = transition.find('attributes')
            trans_attr = {}
            for child in attr:
                if child.text is not None:
                    trans_attr[child.tag] = child.text
            trans_attr = convert_xml_attr(trans_attr)
            log.info(trans_attr)
            mts._add_transition(src=src, dest=dest, label=label, **trans_attr)
        except (AttributeError, ValueError) as e:
            log.warning(f'Expected attribute tag in xml: on transition {src} -{label}-> {dest}: {e}')
            mts._add_transition(src=src, dest=dest, label=label)

    return mts


def convert_xml_attr(keys: Mapping):
    res = {}
    map_keys = {
        'isMay': ('may', lambda x: bool(strtobool(x))),
        'isMust': ('must', lambda x: bool(strtobool(x))),
        'isGreen': ('green', lambda x: bool(strtobool(x))),
        'isRed': ('red', lambda x: bool(strtobool(x))),
        'memberId': ('memberId', lambda x: int(x))
    }
    for xml_key, (norm_key, func) in map_keys.items():
        if xml_key in keys:
            res[norm_key] = func(keys[xml_key])

    return res
