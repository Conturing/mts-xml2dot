from typing import Mapping


class MTS:

    def __init__(self):
        self.states = []
        self.transitions = []

    def add_state(self, id, initial: bool = False):
        self._add_state({
            'id': id,
            'initial': initial
        })

    def _add_state(self, state: Mapping):
        self.states.append(state)

    def add_transition(self, src, dest, label, may: bool, must: bool, green: bool, red: bool):
        self._add_transition({
            'src': src,
            'dest': dest,
            'label': label,
            'may': may,
            'must': must,
            'green': green,
            'red': red
        })

    def _add_transition(self, transition: Mapping):
        self.transitions.append(transition)
