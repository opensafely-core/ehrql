import csv
import dataclasses
import importlib.util
import pathlib
import shutil
import subprocess
import sys
from collections import Mapping
from contextlib import contextmanager, nullcontext

import networkx as nx
import structlog

from databuilder.column_specs import get_column_specs
from databuilder.itertools_utils import eager_iterator
from databuilder.query_language import Dataset
from databuilder.sqlalchemy_utils import clause_as_str, get_setup_and_cleanup_queries

from . import query_language as ql
from .query_model import Case, all_nodes, get_input_nodes
from .validate_dummy_data import validate_dummy_data_file, validate_file_types_match

log = structlog.getLogger()


def generate_dataset(
    definition_file,
    dataset_file,
    db_url,
    backend_id,
    query_engine_id,
    environ,
):
    log.info(f"Generating dataset for {str(definition_file)}")

    dataset_definition = load_definition(definition_file)
    variable_definitions = ql.compile(dataset_definition)
    column_specs = get_column_specs(variable_definitions)

    query_engine = get_query_engine(db_url, backend_id, query_engine_id, environ)
    results = query_engine.get_results(variable_definitions)
    # Because `results` is a generator we won't actually execute any queries until we
    # start consuming it. But we want to make sure we trigger any errors (or relevant
    # log output) before we create the output file. Wrapping the generator in
    # `eager_iterator` ensures this happens by consuming the first item upfront.
    results = eager_iterator(results)
    write_dataset_csv(column_specs, results, dataset_file)


def pass_dummy_data(definition_file, dataset_file, dummy_data_file):
    log.info(f"Generating dataset for {str(definition_file)}")

    dataset_definition = load_definition(definition_file)
    validate_dummy_data_file(dataset_definition, dummy_data_file)
    validate_file_types_match(dummy_data_file, dataset_file)

    dataset_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(dummy_data_file, dataset_file)


def dump_dataset_sql(
    definition_file, output_file, backend_id, query_engine_id, environ
):
    log.info(f"Generating SQL for {str(definition_file)}")

    dataset_definition = load_definition(definition_file)
    query_engine = get_query_engine(None, backend_id, query_engine_id, environ)

    variable_definitions = ql.compile(dataset_definition)
    all_query_strings = get_sql_strings(query_engine, variable_definitions)
    log.info("SQL generation succeeded")

    with open_output_file(output_file) as f:
        for query_str in all_query_strings:
            f.write(f"{query_str};\n\n")


def positive_hash(node):
    return hash(node) & sys.maxsize


def to_nx_node(node):
    def should_ignore(name, value):
        return (
            value in get_input_nodes(node)
            or (name == "schema" and isinstance(value, Mapping))
            or (isinstance(node, Case) and name == "cases")
        )

    args = [
        value
        for name, value in [
            (name, getattr(node, name))
            for name in [f.name for f in dataclasses.fields(node)]
        ]
        if not should_ignore(name, value)
    ]

    return positive_hash(node), type(node).__name__, tuple(args)


def nx_node_for_variable(name):
    if name == "population":
        return positive_hash(name), "Population", ()
    return positive_hash(name), "Variable", (name,)


def as_nx_graph(variable_definitions):
    # This is currently not an isomorphism because we throw away the attribute names (which would clutter up the
    # visual representation). It would be straightforward to add them to this encoding, though; for subnodes we could
    # decorate the edges with a "type" property and for other attributes we could store them in a dict rather than a
    # tuple. Then we'd have an isomorphism and could freely transform in either direction without losing anything.
    g = nx.DiGraph()
    for name, definition in variable_definitions.items():
        g.add_edge(nx_node_for_variable(name), to_nx_node(definition))
        for node in all_nodes(definition):
            for subnode in get_input_nodes(node):
                g.add_edge(to_nx_node(node), to_nx_node(subnode))
    return g


def is_node_type(node, *types):
    _, type_, _ = node
    return type_ in types


def is_variable_ish(node):
    return is_node_type(node, "Variable", "Population")


def is_table_ish(node):
    return is_node_type(node, "SelectTable", "SelectPatientTable")


def file_for_variable(node):
    _, type_, args = node
    if type_ == "Population":
        name = "population"
    else:
        (name,) = args
    return f"{name}.svg"


def write_svg(graph, output_path):
    def truncate(s, limit):
        if len(s) <= limit:
            return s
        return s[: limit - 3] + "..."

    dot_lines = []

    def write(s, indent=0):
        dot_lines.append("\t" * indent + s + "\n")

    def write_node(node, indent):
        id_, type_, args = node

        if is_variable_ish(node):
            url_fragment = f'URL="{file_for_variable(node)}",'
        else:
            url_fragment = ""

        args = [truncate(str(arg), 20) for arg in args]
        style = (
            "filled, rounded"
            if is_variable_ish(node) or is_table_ish(node)
            else "rounded"
        )
        write(
            f'{id_} [label="{type_}({",".join(args)})", {url_fragment} style="{style}", shape=box]',
            indent,
        )

    def write_edge(edge, indent):
        frm, to, virtual = edge
        frm_id, _, _ = frm
        to_id, _, _ = to
        colour = "lightgrey" if virtual else "black"
        write(f"{frm_id} -> {to_id} [color={colour}]", indent)

    def partition(nodes):
        sources, others, sinks = [], [], []
        for node in nodes:
            if is_variable_ish(node):
                sources.append(node)
            elif is_table_ish(node):
                sinks.append(node)
            else:
                others.append(node)
        return sources, others, sinks

    sources, others, sinks = partition(graph.nodes)

    write("digraph {")

    write("{", indent=1)
    write("rank=source", indent=2)
    for node in sources:
        write_node(node, indent=2)
    write("}", indent=1)

    for node in others:
        write_node(node, indent=1)

    write("{", indent=1)
    write("rank=sink", indent=2)
    for node in sinks:
        write_node(node, indent=2)
    write("}", indent=1)

    for edge in graph.edges.data("virtual"):
        write_edge(edge, indent=1)

    write("}")

    output_file = open(output_path, mode="w")
    dot_process = subprocess.Popen(
        ["dot", "-Tsvg"], stdin=subprocess.PIPE, stdout=output_file
    )
    dot_process.communicate("".join(dot_lines).encode())
    if not dot_process.returncode == 0:
        raise Exception(f"dot failed: {dot_process.returncode}")


def graph_query(definition_file, output_dir):
    log.info(f"Graphing query for {str(definition_file)}")

    output_dir = pathlib.Path(output_dir)

    dataset_definition = load_definition(definition_file)
    variable_definitions = ql.compile(dataset_definition)

    graph = as_nx_graph(variable_definitions)

    variables = nx.subgraph_view(graph, filter_node=is_variable_ish).nodes

    for variable in variables:
        descendants = nx.descendants(graph, variable)

        variable_subgraph = graph.subgraph(
            {variable} | descendants
        ).copy()  # we're going to modify, so make a copy
        rest_of_graph = graph.copy()
        rest_of_graph.remove_edges_from(variable_subgraph.edges)
        rest_of_graph_reversed = rest_of_graph.reverse()

        related_variables = set()
        for descendant in descendants:
            desc_type, _, _ = descendant
            if desc_type == "Value":
                continue

            for other_variable in variables - {variable}:
                if nx.has_path(rest_of_graph_reversed, descendant, other_variable):
                    related_variables.add(other_variable)
                    variable_subgraph.add_edge(other_variable, descendant, virtual=True)

        file_name = file_for_variable(variable)
        write_svg(variable_subgraph, output_dir / file_name)


def get_sql_strings(query_engine, variable_definitions):
    results_query = query_engine.get_query(variable_definitions)
    setup_queries, cleanup_queries = get_setup_and_cleanup_queries(results_query)
    dialect = query_engine.sqlalchemy_dialect()
    sql_strings = []

    for n, query in enumerate(setup_queries, start=1):
        sql = clause_as_str(query, dialect)
        sql_strings.append(f"-- Setup query {n:03} / {len(setup_queries):03}\n{sql}")

    sql = clause_as_str(results_query, dialect)
    sql_strings.append(f"-- Results query\n{sql}")

    assert not cleanup_queries, "Support these once tests exercise them"

    return sql_strings


def open_output_file(output_file):
    # If a file path is supplied, create it and open for writing
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        return output_file.open(mode="w")
    # Otherwise return `stdout` wrapped in a no-op context manager
    else:
        return nullcontext(sys.stdout)


def get_query_engine(dsn, backend_id, query_engine_id, environ):
    # Load backend if supplied
    if backend_id:
        backend = import_string(backend_id)()
    else:
        backend = None

    # If there's an explictly specified query engine class use that
    if query_engine_id:
        query_engine_class = import_string(query_engine_id)
    # Otherwise use whatever the backend specifies
    elif backend:
        query_engine_class = backend.query_engine_class
    # Default to using CSV query engine
    else:
        query_engine_class = import_string(
            "databuilder.query_engines.csv.CSVQueryEngine"
        )

    return query_engine_class(dsn=dsn, backend=backend, config=environ)


def generate_measures(
    definition_path, input_file, dataset_file
):  # pragma: no cover (measures not implemented)
    raise NotImplementedError


def test_connection(backend_id, url, environ):
    from sqlalchemy import select

    backend = import_string(backend_id)()
    query_engine = backend.query_engine_class(url, backend, config=environ)
    with query_engine.engine.connect() as connection:
        connection.execute(select(1))
    print("SUCCESS")


def load_definition(definition_file):
    module = load_module(definition_file)
    try:
        dataset = module.dataset
    except AttributeError:
        raise AttributeError("A dataset definition must define one 'dataset'")
    assert isinstance(
        dataset, Dataset
    ), "'dataset' must be an instance of databuilder.query_language.Dataset()"
    return dataset


def load_module(definition_path):
    # Taken from the official recipe for importing a module from a file path:
    # https://docs.python.org/3.9/library/importlib.html#importing-a-source-file-directly

    # The name we give the module is arbitrary
    spec = importlib.util.spec_from_file_location("dataset", definition_path)
    module = importlib.util.module_from_spec(spec)
    # Temporarily add the directory containing the definition to the path so that the
    # definition can import library modules from that directory
    with add_to_sys_path(str(definition_path.parent)):
        spec.loader.exec_module(module)
    return module


@contextmanager
def add_to_sys_path(directory):
    original = sys.path.copy()
    sys.path.append(directory)
    try:
        yield
    finally:
        sys.path = original


def import_string(dotted_path):
    module_name, _, attribute_name = dotted_path.rpartition(".")
    module = importlib.import_module(module_name)
    return getattr(module, attribute_name)


def write_dataset_csv(column_specs, results, dataset_file):
    headers = list(column_specs.keys())
    dataset_file.parent.mkdir(parents=True, exist_ok=True)
    with dataset_file.open(mode="w") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(results)
