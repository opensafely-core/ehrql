import importlib.util
import os
import subprocess
import sys
from pathlib import Path

from ehrql.measures import Measures
from ehrql.query_language import Dataset, compile
from ehrql.serializer import deserialize
from ehrql.utils.traceback_utils import get_trimmed_traceback


class DefinitionError(Exception):
    "Error in or with the user-supplied definition file"


def load_dataset_definition(definition_file, user_args):
    return load_definition_in_subprocess("dataset", definition_file, user_args)


def load_measure_definitions(definition_file, user_args):
    return load_definition_in_subprocess("measures", definition_file, user_args)


def load_definition_in_subprocess(definition_type, definition_file, user_args):
    PLEDGE_BIN = Path(__file__).parents[1] / "bin" / "pledge"
    result = subprocess.run(
        [
            PLEDGE_BIN,
            # "-q",
            "-p",
            # "stdio rpath wpath cpath prot_exec tty",
            "stdio rpath prot_exec tty",
            "-v",
            "r:/",
            # "-v",
            # "r:" + str(Path(sys.executable).parents[1]),
            # "-v",
            # "r:" + str(Path(__file__).parents[1]),
            # "-v",
            # "rwc:{os.getcwd()}",
            sys.executable,
            "-m",
            "ehrql",
            "serialize-definition",
            "--definition-type",
            definition_type,
            definition_file,
            "--",
            *user_args,
        ],
        env={
            "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
            "PYTHONHASHSEED": "0",
        },
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise DefinitionError(result.stderr)
    else:
        print(result.stderr, file=sys.stderr, end="")
    return deserialize(result.stdout)


def load_dataset_definition_unsafe(definition_file, user_args):
    module = load_module(definition_file, user_args)
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
    variable_definitions = compile(dataset)
    return variable_definitions, dataset.dummy_data_config


def load_measure_definitions_unsafe(definition_file, user_args):
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


DEFINITION_LOADERS = {
    "dataset": load_dataset_definition_unsafe,
    "measures": load_measure_definitions_unsafe,
}


def load_definition_unsafe(definition_type, definition_file, user_args):
    return DEFINITION_LOADERS[definition_type](definition_file, user_args)


def load_test_data(definition_file, user_args):
    module = load_module(definition_file, user_args)
    return module.patient_data


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
