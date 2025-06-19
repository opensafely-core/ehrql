import json
import logging
import os
import shutil
import sys
from contextlib import nullcontext
from pathlib import Path

from ehrql import assurance
from ehrql.dummy_data import DummyDataGenerator
from ehrql.dummy_data_nextgen import DummyDataGenerator as NextGenDummyDataGenerator
from ehrql.dummy_data_nextgen import (
    DummyMeasuresDataGenerator as NextGenDummyMeasuresDataGenerator,
)
from ehrql.file_formats import (
    output_filename_supports_multiple_tables,
    read_rows,
    read_tables,
    split_directory_and_extension,
    write_rows,
    write_tables,
)
from ehrql.loaders import (
    isolation_report,
    load_dataset_definition,
    load_debug_definition,
    load_definition_unsafe,
    load_measure_definitions,
    load_test_definition,
)
from ehrql.measures import (
    DummyMeasuresDataGenerator,
    apply_sdc_to_measure_results,
    get_column_specs_for_measures,
    get_measure_results,
    get_table_specs_for_measures,
    split_measure_results_into_tables,
)
from ehrql.query_engines.local_file import LocalFileQueryEngine
from ehrql.query_engines.sqlite import SQLiteQueryEngine
from ehrql.query_model.column_specs import (
    get_column_specs_from_schema,
    get_table_specs,
)
from ehrql.query_model.graphs import graph_to_svg
from ehrql.serializer import serialize
from ehrql.utils.sqlalchemy_query_utils import clause_as_str


log = logging.getLogger()


def generate_dataset(
    definition_file,
    output_file,
    *,
    dsn,
    backend_class,
    query_engine_class,
    dummy_tables_path,
    dummy_data_file,
    test_data_file,
    environ,
    user_args,
):
    log.info(f"Compiling dataset definition from {str(definition_file)}")
    dataset, dummy_data_config = load_dataset_definition(
        definition_file, user_args, environ
    )

    if test_data_file:
        log.info(f"Testing dataset definition with tests in {str(definition_file)}")
        assure(test_data_file, environ=environ, user_args=user_args)

    table_specs = get_table_specs(dataset)

    if dsn:
        log.info("Generating dataset")
        results_tables = generate_dataset_with_dsn(
            dataset=dataset,
            dsn=dsn,
            backend_class=backend_class,
            query_engine_class=query_engine_class,
            environ=environ,
        )
    else:
        log.info("Generating dummy dataset")
        results_tables = generate_dataset_with_dummy_data(
            dataset=dataset,
            dummy_data_config=dummy_data_config,
            table_specs=table_specs,
            dummy_data_file=dummy_data_file,
            dummy_tables_path=dummy_tables_path,
        )

    write_tables(output_file, results_tables, table_specs)


def generate_dataset_with_dsn(
    *, dataset, dsn, backend_class, query_engine_class, environ
):
    query_engine = get_query_engine(
        dsn,
        backend_class,
        query_engine_class,
        environ,
        default_query_engine_class=LocalFileQueryEngine,
    )
    return query_engine.get_results_tables(dataset)


def generate_dataset_with_dummy_data(
    *, dataset, dummy_data_config, table_specs, dummy_data_file, dummy_tables_path
):
    if dummy_data_file:
        log.info(f"Reading dummy data from {dummy_data_file}")
        return read_tables(dummy_data_file, table_specs)
    elif dummy_tables_path:
        log.info(f"Reading table data from {dummy_tables_path}")
        query_engine = LocalFileQueryEngine(dummy_tables_path)
        return query_engine.get_results_tables(dataset)
    else:
        generator = get_dummy_data_generator(dataset, dummy_data_config)
        return generator.get_results_tables()


def create_dummy_tables(definition_file, dummy_tables_path, user_args, environ):
    log.info(f"Creating dummy data tables for {str(definition_file)}")
    dataset, dummy_data_config = load_dataset_definition(
        definition_file, user_args, environ
    )
    generator = get_dummy_data_generator(dataset, dummy_data_config)
    table_data = generator.get_data()

    if dummy_tables_path is not None:
        directory, extension = split_directory_and_extension(dummy_tables_path)
        log.info(f"Writing tables as '{extension}' files to '{directory}'")

    table_specs = {
        table.name: get_column_specs_from_schema(table.schema)
        for table in table_data.keys()
    }
    write_tables(dummy_tables_path, table_data.values(), table_specs)


def get_dummy_data_generator(dataset, dummy_data_config):
    if dummy_data_config.legacy:
        return DummyDataGenerator(
            dataset,
            population_size=dummy_data_config.population_size,
            timeout=dummy_data_config.timeout,
        )
    else:
        return NextGenDummyDataGenerator(dataset, configuration=dummy_data_config)


def dump_dataset_sql(
    definition_file, output_file, backend_class, query_engine_class, environ, user_args
):
    log.info(f"Generating SQL for {str(definition_file)}")

    dataset, _ = load_dataset_definition(definition_file, user_args, environ)
    query_engine = get_query_engine(
        None,
        backend_class,
        query_engine_class,
        environ,
        default_query_engine_class=SQLiteQueryEngine,
    )

    all_query_strings = get_sql_strings(query_engine, dataset)
    log.info("SQL generation succeeded")

    with open_output_file(output_file) as f:
        for query_str in all_query_strings:
            f.write(f"{query_str};\n\n")


def get_sql_strings(query_engine, dataset):
    queries = query_engine.get_queries(dataset)
    dialect = query_engine.sqlalchemy_dialect()
    sql_strings = []

    for i, (has_results, query) in enumerate(queries, start=1):
        description = "Fetch results from" if has_results else "Run"
        sql = clause_as_str(query, dialect)
        sql_strings.append(f"-- {description} query {i:03} / {len(queries):03}\n{sql}")

    return sql_strings


def open_output_file(output_file):
    # If a file path is supplied, create it and open for writing
    if output_file is not None:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        return output_file.open("w")
    # Otherwise return `stdout` wrapped in a no-op context manager
    else:
        return nullcontext(sys.stdout)


def get_query_engine(
    dsn, backend_class, query_engine_class, environ, default_query_engine_class
):
    # Construct backend if supplied
    if backend_class:
        backend = backend_class(config=environ)
    else:
        backend = None

    if not query_engine_class:
        # Use the query engine class specified by the backend, if we have one
        if backend:
            query_engine_class = backend.query_engine_class
        # Otherwise default to using SQLite
        else:
            query_engine_class = default_query_engine_class

    return query_engine_class(dsn=dsn, backend=backend, config=environ)


def generate_measures(
    definition_file,
    output_file,
    *,
    dsn,
    backend_class,
    query_engine_class,
    dummy_tables_path,
    dummy_data_file,
    environ,
    user_args,
):
    log.info(f"Compiling measure definitions from {str(definition_file)}")
    (
        measure_definitions,
        dummy_data_config,
        disclosure_control_config,
    ) = load_measure_definitions(definition_file, user_args, environ)

    if dsn:
        log.info("Generating measures data")
        results = generate_measures_with_dsn(
            measure_definitions,
            dsn,
            backend_class=backend_class,
            query_engine_class=query_engine_class,
            environ=environ,
        )
    else:
        log.info("Generating dummy measures data")
        results = generate_measures_with_dummy_data(
            measure_definitions,
            dummy_data_config,
            dummy_tables_path=dummy_tables_path,
            dummy_data_file=dummy_data_file,
        )

    if disclosure_control_config.enabled:
        results = apply_sdc_to_measure_results(results)

    write_measure_results(output_file, results, measure_definitions)


def generate_measures_with_dsn(
    measure_definitions,
    dsn,
    backend_class,
    query_engine_class,
    environ,
):
    query_engine = get_query_engine(
        dsn,
        backend_class,
        query_engine_class,
        environ,
        default_query_engine_class=LocalFileQueryEngine,
    )
    return get_measure_results(query_engine, measure_definitions)


def generate_measures_with_dummy_data(
    measure_definitions,
    dummy_data_config,
    dummy_tables_path=None,
    dummy_data_file=None,
):
    if dummy_data_file:
        log.info(f"Reading dummy data from {dummy_data_file}")
        column_specs = get_column_specs_for_measures(measure_definitions)
        return read_rows(dummy_data_file, column_specs)
    elif dummy_tables_path:
        log.info(f"Reading data from {dummy_tables_path}")
        query_engine = LocalFileQueryEngine(dummy_tables_path)
        return get_measure_results(query_engine, measure_definitions)
    else:
        generator = get_dummy_measures_data_class(dummy_data_config)(
            measure_definitions, dummy_data_config
        )
        return generator.get_results()


def get_dummy_measures_data_class(dummy_data_config):
    if dummy_data_config.legacy:
        return DummyMeasuresDataGenerator
    else:
        return NextGenDummyMeasuresDataGenerator


def write_measure_results(output_file, results, measure_definitions):
    column_specs = get_column_specs_for_measures(measure_definitions)
    # Although an `output_file` of `None` (i.e. ouput to console) does support multiple
    # output tables, for consistency with previous behaviour we want to continue writing
    # results to the console as a single combined table. We might revisit this decision
    # but it seems the least surprising thing for now.
    if output_file is None or not output_filename_supports_multiple_tables(output_file):
        write_rows(output_file, results, column_specs)
    else:
        table_specs = get_table_specs_for_measures(measure_definitions)
        tables = split_measure_results_into_tables(results, column_specs, table_specs)
        write_tables(output_file, tables, table_specs)


def assure(test_data_file, environ, user_args):
    dataset, test_data = load_test_definition(test_data_file, user_args, environ)
    results = assurance.validate(dataset, test_data)
    print(assurance.present(results))


def debug_dataset_definition(
    definition_file,
    *,
    environ,
    user_args,
    dummy_tables_path=None,
    render_format="ascii",
):
    # Loading the definition file will execute any show() commands and write
    # the output to stderr.
    load_debug_definition(
        definition_file, user_args, environ, dummy_tables_path, render_format
    )


def test_connection(backend_class, url, environ):
    from sqlalchemy import select

    backend = backend_class()
    query_engine = backend.query_engine_class(url, backend, config=environ)
    with query_engine.engine.connect() as connection:
        connection.execute(select(1))
    print("SUCCESS")


def dump_example_data(environ):
    src_path = Path(__file__).parent / "example-data"
    dst_path = Path(os.getcwd()) / "example-data"
    shutil.copytree(src_path, dst_path, dirs_exist_ok=True)


def serialize_definition(
    definition_type,
    definition_file,
    output_file,
    user_args,
    environ,
    dummy_tables_path=None,
    render_format=None,
):
    result = load_definition_unsafe(
        definition_type,
        definition_file,
        user_args,
        environ,
        dummy_tables_path=dummy_tables_path,
        render_format=render_format,
    )
    with open_output_file(output_file) as f:
        f.write(serialize(result))


def run_isolation_report():
    print(json.dumps(isolation_report(Path.cwd()), indent=4))


def graph_query(definition_file, output_file, environ, user_args):  # pragma: no cover
    log.info(f"Graphing query for {str(definition_file)}")
    dataset, _ = load_dataset_definition(definition_file, user_args, environ)
    graph_to_svg(dataset, output_file)
