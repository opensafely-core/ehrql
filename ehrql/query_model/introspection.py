from ehrql.query_model.nodes import SelectPatientTable, SelectTable, get_input_nodes


def all_nodes(tree):  # pragma: no cover
    nodes = []

    for subnode in get_input_nodes(tree):
        for node in all_nodes(subnode):
            nodes.append(node)
    return [tree] + nodes


def count_nodes(tree):  # pragma: no cover
    return len(all_nodes(tree))


def node_types(tree):  # pragma: no cover
    return [type(node) for node in all_nodes(tree)]


def all_unique_nodes(*nodes):
    found = set()
    for node in nodes:
        gather_unique_nodes(node, found)
    return found


def gather_unique_nodes(node, found):
    found.add(node)
    for subnode in get_input_nodes(node):
        if subnode not in found:
            gather_unique_nodes(subnode, found)


def get_table_nodes(*nodes):
    return {
        subnode
        for subnode in all_unique_nodes(*nodes)
        if isinstance(subnode, SelectTable | SelectPatientTable)
    }
