from mts import MTS
from lark import Lark, Transformer

grammar = Lark(r"""
graph: "strict"? ("graph" | "digraph") id? "{" stmt_list "}"
stmt_list: (stmt ";"?)*
?stmt: node_stmt
 | edge_stmt
 | attr_stmt
 | ass
 | subgraph
attr_stmt: ("graph" | "node" | "edge") attr_list
attr_list: ("[" a_list? "]")+
a_list: (ass (";" | ",")?)+
ass: id "=" id
edge_stmt: (node_id | subgraph) edgerhs attr_list?
edgerhs: (EDGE_OP (node_id | subgraph))+
node_stmt: node_id attr_list?
?node_id: id
subgraph: ("subgraph" id?)? "{" stmt_list "}"

id: RAW_ID | ESCAPED_STRING

EDGE_OP: "->" | "--"
RAW_ID: /[_a-zA-Z\200-\377][a-zA-Z0-9\200-\377_]*/

%import common.ESCAPED_STRING
%import common.SIGNED_NUMBER
%import common.WS
%ignore WS

""", start='graph')


class DotTransformer(Transformer):
    def graph(self, items):
        name, stmts = items
        return name, stmts

    def ass(self, key_val):
        key, value = key_val
        return key, value

    def a_list(self, items):
        attr = {}
        for k, v in items:
            attr[k] = v
        return attr

    def stmt_list(self, items):
        return items

    def attr_list(self, items):
        attr = dict()
        for d in items:
            attr = {**attr, **d}
        return attr

    def edge_stmt(self, items):
        if len(items) == 3:
            src, rhs, attr = items
        else:
            src, rhs = items
            attr = {}
        dest = rhs.children[1]
        return 'EDGE', {'src': src, 'dest': dest, 'attr': attr}

    def node_stmt(self, val):
        id, attr = val
        return 'NODE', {'id': id, 'attr': attr}

    def id(self, val):
        return val[0]

    def RAW_ID(self, val):
        return val.value

    def ESCAPED_STRING(self, val):
        return val.value


def parse_dot(path):
    parser = grammar
    with open(path, 'rt') as f:
        tree = parser.parse(f.read())

        mts = MTS()
        name, graph_attr = DotTransformer(visit_tokens=True).transform(tree)
        for type, node_attr in graph_attr:
            if type == 'NODE':
                mts._add_state(id=node_attr["id"], **node_attr["attr"])
            elif type == 'EDGE':
                mts._add_transition(src=node_attr["src"], dest=node_attr["dest"], **node_attr["attr"])
            else:
                raise ValueError("Unexpected type in graph.")

    return mts


