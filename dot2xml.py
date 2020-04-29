from mts import MTS


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