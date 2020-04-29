from distutils.util import strtobool
from xml.etree import ElementTree as ET
import logging

from mts import MTS

log = logging.getLogger(__name__)


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
        attr  = transition.find('attributes')
        may   = bool(strtobool(attr.find('isMay').text))
        must  = bool(strtobool(attr.find('isMust').text))
        green = bool(strtobool(attr.find('isGreen').text))
        red   = bool(strtobool(attr.find('isRed').text))
        mts.add_transition(src, dest, label, may, must, green, red)

    return mts