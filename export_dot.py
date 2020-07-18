from mts import MTS
import logging
from itertools import chain

log = logging.getLogger(__name__)


def modal_to_dot(path, mts: MTS, mc: bool = False, derive_groups: bool = False):
    class_text = 'digraph'

    states = []
    state_mapping = {}
    uid = 0

    initial_states = list(mts.state_view(lambda x: x['initial'], lambda x: x))
    if len(initial_states) != 1:
        log.warning(f'Found multiple initial states: {initial_states}')

    for state in sorted(mts.states, key=lambda x: 0 if x['initial'] else 1):
        state_mapping[state['id']] = uid
        states.append(
            's{id} [shape="circle" label="{label}"];'.format(id=uid, label=state['id'])
        )
        uid += 1

    red_transitions = 0

    def derive_group(transition):
        nonlocal red_transitions
        if transition['green']:
            return 0
        elif transition['red']:
            red_transitions += 1
            return red_transitions
        else:
            return -1

    transitions = []
    for transition in mts.transitions:
        transitions.append(
            gen_mts_transition(state_mapping, transition) if not mc else
            gen_mc_transition(state_mapping, transition, **{'group': derive_group(transition)} if derive_groups else {})
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


def gen_mts_transition(state_mapping, transition):
    return 's{src} -> s{dest} [modality="{mod}", style="{style}", label="{label}"];'.format(
        src=state_mapping[transition["src"]],
        dest=state_mapping[transition["dest"]],
        mod="MUST" if transition["must"] else "MAY",
        style="strict" if transition["must"] else "dashed",
        label=transition["label"]
    )


def gen_mc_transition(state_mapping, transition, **kwargs):
    options = {
        'src': state_mapping[transition["src"]],
        'dest': state_mapping[transition["dest"]],
        'mod': "MUST" if transition["must"] else "MAY",
        'style': "strict" if transition["must"] else "dashed",
        'label': transition["label"],
        'color': 'color="green"' if transition["green"] else
        ('color="red"' if transition["red"] else ''),
        'contract': 'GREEN' if transition["green"] else
        ('RED' if transition["red"] else 'NONE'),
        'group': transition["group"] if "group" in transition else "-1"
    }

    options.update(kwargs)

    return 's{src} -> s{dest} [modality="{mod}", style="{style}", {color} contract="{contract}", group="{group}", label="{label}"];'.format(
        **options
    )