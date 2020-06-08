from typing import Mapping, Callable, Any, Sequence, Iterator


class MTS:

    def __init__(self):
        self.states = []
        self.transitions = []

    def add_state(self, id, initial: bool):
        self._add_state(**{
            'id': id,
            'initial': initial
        })

    def _add_state(self, **state: Mapping):
        options = {
            'initial': False
        }
        options.update(state)
        self.states.append(state)

    def state_view(self, predicate: Callable[[Mapping], bool], transformer: Callable[[Mapping], Any] = lambda x: x.get('id')) -> Iterator[Any]:
        return map(transformer, filter(predicate, self.states))

    def add_transition(self, src, dest, label, may: bool, must: bool, green: bool, red: bool):
        self._add_transition(**{
            'src': src,
            'dest': dest,
            'label': label,
            'may': may,
            'must': must,
            'green': green,
            'red': red
        })

    def _add_transition(self, **transition: Mapping):
        options = {
            'may': True,
            'must': False,
            'green': False,
            'red': False
        }
        options.update(transition)
        self.transitions.append(options)
