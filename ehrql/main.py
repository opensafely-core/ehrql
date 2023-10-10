import importlib.util
import os
import shutil
import sys
from contextlib import nullcontext
from pathlib import Path

import structlog

from ehrql import assurance, sandbox
from ehrql.dummy_data import DummyDataGenerator
from ehrql.file_formats import read_dataset, write_dataset
from ehrql.measures import (
    DummyMeasuresDataGenerator,
    Measures,
    get_column_specs_for_measures,
    get_measure_results,
)
from ehrql.query_engines.csv import CSVQueryEngine
from ehrql.query_engines.sqlite import SQLiteQueryEngine
from ehrql.query_language import Dataset, compile
from ehrql.query_model.column_specs import get_column_specs
from ehrql.utils.itertools_utils import eager_iterator
from ehrql.utils.orm_utils import write_orm_models_to_csv_directory
from ehrql.utils.sqlalchemy_query_utils import (
    clause_as_str,
    get_setup_and_cleanup_queries,
)
from ehrql.utils.traceback_utils import get_trimmed_traceback


log = structlog.getLogger()


class DefinitionError(Exception):
    "Error in or with the user-supplied definition file"


def generate_dataset(
    definition_file,
    dataset_file,
    dsn=None,
    backend_class=None,
    query_engine_class=None,
    dummy_tables_path=None,
    dummy_data_file=None,
    environ=None,
    user_args=(),
):
    log.info(f"Compiling dataset definition from {str(definition_file)}")
    variable_definitions, dummy_data_config = load_dataset_definition(
        definition_file, user_args
    )

    if dsn:
        generate_dataset_with_dsn(
            variable_definitions,
            dataset_file,
            dsn,
            backend_class=backend_class,
            query_engine_class=query_engine_class,
            environ=environ or {},
        )
    else:
        generate_dataset_with_dummy_data(
            variable_definitions,
            dummy_data_config,
            dataset_file,
            dummy_data_file,
            dummy_tables_path,
        )


def generate_dataset_with_dsn(
    variable_definitions, dataset_file, dsn, backend_class, query_engine_class, environ
):
    log.info("Generating dataset")
    column_specs = get_column_specs(variable_definitions)

    query_engine = get_query_engine(
        dsn,
        backend_class,
        query_engine_class,
        environ,
        default_query_engine_class=CSVQueryEngine,
    )
    results = query_engine.get_results(variable_definitions)
    # Because `results` is a generator we won't actually execute any queries until we
    # start consuming it. But we want to make sure we trigger any errors (or relevant
    # log output) before we create the output file. Wrapping the generator in
    # `eager_iterator` ensures this happens by consuming the first item upfront.
    results = eager_iterator(results)
    write_dataset(dataset_file, results, column_specs)


def generate_dataset_with_dummy_data(
    variable_definitions,
    dummy_data_config,
    dataset_file,
    dummy_data_file=None,
    dummy_tables_path=None,
):
    log.info("Generating dummy dataset")
    column_specs = get_column_specs(variable_definitions)

    if dummy_data_file:
        log.info(f"Reading dummy data from {dummy_data_file}")
        reader = read_dataset(dummy_data_file, column_specs)
        results = iter(reader)
    elif dummy_tables_path:
        log.info(f"Reading CSV data from {dummy_tables_path}")
        query_engine = CSVQueryEngine(dummy_tables_path)
        results = query_engine.get_results(variable_definitions)
    else:
        generator = DummyDataGenerator(
            variable_definitions,
            population_size=dummy_data_config.population_size,
        )
        results = generator.get_results()

    log.info("Building dataset and writing results")
    results = eager_iterator(results)
    write_dataset(dataset_file, results, column_specs)


def create_dummy_tables(definition_file, dummy_tables_path, user_args):
    log.info(f"Creating dummy data tables for {str(definition_file)}")
    variable_definitions, dummy_data_config = load_dataset_definition(
        definition_file, user_args
    )
    generator = DummyDataGenerator(
        variable_definitions,
        population_size=dummy_data_config.population_size,
    )
    dummy_tables = generator.get_data()
    dummy_tables_path.parent.mkdir(parents=True, exist_ok=True)
    log.info(f"Writing CSV files to {dummy_tables_path}")
    write_orm_models_to_csv_directory(dummy_tables_path, dummy_tables)


def dump_dataset_sql(
    definition_file, output_file, backend_class, query_engine_class, environ, user_args
):
    log.info(f"Generating SQL for {str(definition_file)}")

    variable_definitions, _ = load_dataset_definition(definition_file, user_args)
    query_engine = get_query_engine(
        None,
        backend_class,
        query_engine_class,
        environ,
        default_query_engine_class=SQLiteQueryEngine,
    )

    all_query_strings = get_sql_strings(query_engine, variable_definitions)
    log.info("SQL generation succeeded")

    with open_output_file(output_file) as f:
        for query_str in all_query_strings:
            f.write(f"{query_str};\n\n")


def get_sql_strings(query_engine, variable_definitions):
    results_query = query_engine.get_query(variable_definitions)
    setup_queries, cleanup_queries = get_setup_and_cleanup_queries(results_query)
    dialect = query_engine.sqlalchemy_dialect()
    sql_strings = []

    for i, query in enumerate(setup_queries, start=1):
        sql = clause_as_str(query, dialect)
        sql_strings.append(f"-- Setup query {i:03} / {len(setup_queries):03}\n{sql}")

    sql = clause_as_str(results_query, dialect)
    sql_strings.append(f"-- Results query\n{sql}")

    for i, query in enumerate(cleanup_queries, start=1):
        sql = clause_as_str(query, dialect)
        sql_strings.append(
            f"-- Cleanup query {i:03} / {len(cleanup_queries):03}\n{sql}"
        )

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
    dsn=None,
    backend_class=None,
    query_engine_class=None,
    dummy_tables_path=None,
    dummy_data_file=None,
    environ=None,
    user_args=(),
):
    log.info(f"Compiling measure definitions from {str(definition_file)}")
    measure_definitions = load_measure_definitions(definition_file, user_args)

    if dsn:
        generate_measures_with_dsn(
            measure_definitions,
            output_file,
            dsn,
            backend_class=backend_class,
            query_engine_class=query_engine_class,
            environ=environ or {},
        )
    else:
        generate_measures_with_dummy_data(
            measure_definitions, output_file, dummy_tables_path, dummy_data_file
        )


def generate_measures_with_dsn(
    measure_definitions, output_file, dsn, backend_class, query_engine_class, environ
):
    log.info("Generating measures data")
    column_specs = get_column_specs_for_measures(measure_definitions)

    query_engine = get_query_engine(
        dsn,
        backend_class,
        query_engine_class,
        environ,
        default_query_engine_class=CSVQueryEngine,
    )
    results = get_measure_results(query_engine, measure_definitions)
    results = eager_iterator(results)
    write_dataset(output_file, results, column_specs)


def generate_measures_with_dummy_data(
    measure_definitions, output_file, dummy_tables_path=None, dummy_data_file=None
):
    log.info("Generating dummy measures data")
    column_specs = get_column_specs_for_measures(measure_definitions)

    if dummy_data_file:
        log.info(f"Reading dummy data from {dummy_data_file}")
        reader = read_dataset(dummy_data_file, column_specs)
        results = iter(reader)
    elif dummy_tables_path:
        log.info(f"Reading CSV data from {dummy_tables_path}")
        query_engine = CSVQueryEngine(dummy_tables_path)
        results = get_measure_results(query_engine, measure_definitions)
    else:
        results = DummyMeasuresDataGenerator(measure_definitions).get_results()

    log.info("Calculating measures and writing results")
    results = eager_iterator(results)
    write_dataset(output_file, results, column_specs)


def run_sandbox(dummy_tables_path, environ):
    sandbox.run(dummy_tables_path)


def assure(test_data_file, environ, user_args):
    variable_definitions, test_data = load_test_definition(test_data_file, user_args)
    results = assurance.validate(variable_definitions, test_data)
    print(assurance.present(results))


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


def load_dataset_definition(definition_file, user_args):
    module = load_module(definition_file, user_args)
    variable_definitions = get_variable_definitions_from_module(module)
    return variable_definitions, module.dataset.dummy_data_config


def load_test_definition(definition_file, user_args):
    module = load_module(definition_file, user_args)
    variable_definitions = get_variable_definitions_from_module(module)
    return variable_definitions, module.patient_data


def get_variable_definitions_from_module(module):
    try:
        dataset = module.dataset
    except AttributeError:
        raise DefinitionError(
            "Did not find a variable called 'dataset' in dataset definition file"
        )
    if not isinstance(dataset, Dataset):
        raise DefinitionError("'dataset' must be an instance of ehrql.Dataset")
    if not hasattr(dataset, "population"):
        raise DefinitionError(
            "A population has not been defined; define one with define_population()"
        )
    return compile(dataset)


def load_measure_definitions(definition_file, user_args):
    module = load_module(definition_file, user_args)
    try:
        measures = module.measures
    except AttributeError:
        raise DefinitionError(
            "Did not find a variable called 'measures' in measures definition file"
        )
    if not isinstance(measures, Measures):
        raise DefinitionError("'measures' must be an instance of ehrql.Measures")
    if len(measures) == 0:
        raise DefinitionError("No measures defined")
    return list(measures)


def load_module(module_path, user_args=()):
    # Taken from the official recipe for importing a module from a file path:
    # https://docs.python.org/3.9/library/importlib.html#importing-a-source-file-directly
    spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
    module = importlib.util.module_from_spec(spec)
    # Temporarily add the directory containing the definition to the start of `sys.path`
    # (just as `python path/to/script.py` would) so that the definition can import
    # library modules from that directory
    original_sys_path = sys.path.copy()
    sys.path.insert(0, str(module_path.parent.absolute()))
    # Temporarily modify `sys.argv` so it contains any user-supplied arguments and
    # generally looks as it would had you run: `python script.py some args --here`
    original_sys_argv = sys.argv.copy()
    sys.argv = [str(module_path), *user_args]
    try:
        spec.loader.exec_module(module)
        return module
    except Exception as exc:
        traceback = get_trimmed_traceback(exc, module.__file__)
        raise DefinitionError(f"Failed to import '{module_path}':\n\n{traceback}")
    finally:
        sys.path = original_sys_path
        sys.argv = original_sys_argv
