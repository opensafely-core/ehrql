from ehrql.query_model.nodes import SelectPatientTable, SelectTable, get_input_nodes


def all_nodes(tree):
    nodes = []

    for subnode in get_input_nodes(tree):
        for node in all_nodes(subnode):
            nodes.append(node)
    return [tree] + nodes


def count_nodes(tree):  # pragma: no cover
    return len(all_nodes(tree))


def node_types(tree):  # pragma: no cover
    return [type(node) for node in all_nodes(tree)]


def get_table_nodes(*nodes):
    table_nodes = set()
    for node in nodes:
        for subnode in all_nodes(node):
            if isinstance(subnode, SelectTable | SelectPatientTable):
                table_nodes.add(subnode)
    return table_nodes
