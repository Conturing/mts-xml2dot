import xml

from mts import MTS
import logging
from itertools import chain
import xml.etree.ElementTree as ET

log = logging.getLogger(__name__)


def modal_to_xml(path, mts: MTS, mc: bool = False, derive_groups: bool = False):

    root = ET.Element('modalContract')
    states = ET.SubElement(root, 'states')
    transitions = ET.SubElement(root, 'transitions')

    for state in mts.states:
        state_tag = ET.SubElement(states, 'state')
        id_tag = ET.SubElement(state_tag, 'id')
        attr_tag = ET.SubElement(state_tag, 'attributes')
        id_tag.text = state['id']
        for attr_key, attr_value in state.items():
            if attr_key != 'id':
                tag = ET.SubElement(attr_tag, attr_key)
                tag.text = str(attr_value)

    map_keys = {
        'may': 'isMay',
        'must': 'isMust',
        'green': 'isGreen',
        'red': 'isRed',
        'memberId': 'memberId'
    }

    for transition in mts.transitions:
        trans_tag = ET.SubElement(transitions, 'transition')
        src_tag = ET.SubElement(trans_tag, 'sourceId')
        dest_tag = ET.SubElement(trans_tag, 'targetId')
        label_tag = ET.SubElement(trans_tag, 'label')
        attr_tag = ET.SubElement(trans_tag, 'attributes')
        src_tag.text = transition['src']
        dest_tag.text = transition['dest']
        label_tag.text = transition['label']
        for attr_key, attr_value in transition.items():
            if attr_key not in ['src', 'dest', 'label']:
                tag = ET.SubElement(attr_tag, map_keys.get(attr_key))
                tag.text = str(attr_value)

    tree = ET.ElementTree(root)

    with open(path, 'wt') as f:
        tree.write(f, encoding='unicode', xml_declaration=True)
