import pprint
from distutils.util import strtobool
import xml.etree.ElementTree as ET
import logging
import sys
import datetime as dt

from mts import MTS

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
stdout_handler.setLevel(logging.WARNING)
file_handler = logging.FileHandler(f'log/{dt.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")}.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
file_handler.setLevel(logging.DEBUG)
logging.basicConfig(handlers=[stdout_handler, file_handler])
log = logging.getLogger('log')


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

def mts_to_dot(path, mts: MTS):
    class_text = 'digraph'

    states = []
    state_mapping = {}
    uid = 0
    for state in mts.states:
        state_mapping[state['id']] = uid
        states.append(
            's{id} [shape="circle" label="{label}"];'.format(id=uid, label=state['id'])
        )
        uid += 1

    transitions = []
    for transition in mts.transitions:
        transitions.append(
            's{src} -> s{dest} [modality="{mod}", style="{style}", label="{label}"];'.format(
                src=state_mapping[transition["src"]],
                dest=state_mapping[transition["dest"]],
                mod="MUST" if transition["must"] else "MAY",
                style="dashed",
                label=transition["label"]
            )
        )

    with open(path, 'wt') as f:
        f.write(f'{class_text} g {{\n\n')
        for s in states:
            f.write('\t' + s + '\n')
        f.write('\n')
        for t in transitions:
            f.write('\t' + t + '\n')
        f.write('\n')
        f.write('__start0 [label="" shape="none" width="0" height="0"];\n')
        f.write('__start0 -> s0;\n')
        f.write('}\n')


def mc_to_dot(path, mts: MTS):
    class_text = 'digraph'

    states = []
    state_mapping = {}
    uid = 0
    for state in mts.states:
        state_mapping[state['id']] = uid
        states.append(
            's{id} [shape="circle" label="{label}"];'.format(id=uid, label=state['id'])
        )
        uid += 1

    transitions = []
    for transition in mts.transitions:
        transitions.append(
            's{src} -> s{dest} [modality="{mod}", style="{style}", {color} contract="{contract}", label="{label}"];'.format(
                src=state_mapping[transition["src"]],
                dest=state_mapping[transition["dest"]],
                mod="MUST" if transition["must"] else "MAY",
                style="dashed",
                label=transition["label"],
                color='color="green"' if transition["green"] else
                ('color="red"' if transition["red"] else ''),
                contract='GREEN' if transition["green"] else
                ('RED' if transition["red"] else 'NONE')
            )
        )

    with open(path, 'wt') as f:
        f.write(f'{class_text} g {{\n\n')
        for s in states:
            f.write('\t' + s + '\n')
        f.write('\n')
        for t in transitions:
            f.write('\t' + t + '\n')
        f.write('\n')
        f.write('__start0 [label="" shape="none" width="0" height="0"];\n')
        f.write('__start0 -> s0;\n')
        f.write('}\n')



if __name__ == "__main__":
    mts = parse_xml(path='examples/mts.xml')
    mts_to_dot('mts.dot', mts)
    mts = parse_xml(path='examples/mc2.xml')
    mc_to_dot('mc2.dot', mts)
