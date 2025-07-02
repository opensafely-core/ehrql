import logging
import sys
from argparse import ArgumentParser
from typing import Any


logger = logging.getLogger(__name__)


def get_parameter(name, type: callable = str, default: Any | None = None):  # NOQA: A002
    """
    Define and retrieve user-specified parameters that have been passed on the command line.

    User-definied parameters are passed after a `--`, in the format `--key value`

    For example, to pass values for two parameters, `max_age` and `region`:

    ```
    generate-dataset /path/to/dataset_definiton/.py -- --max_age 70 --sex female
    ```

    Multiple values can be passed per parameter, and will be parsed
    as a list, e.g.
    ```
    generate-dataset /path/to/dataset_definiton/.py -- --sex male female
    ```
    or
    ```
    generate-dataset /path/to/dataset_definiton/.py -- --sex male --sex female
    ```

    For each parameter, in the dataset definition, call `get_parameter()`, e.g.:
    ```
        sex = get_parameter(name="sex")
    ```

    Parameters are parsed as strings, unless a `type` is explicitly specified.
    `type` can be any callable that takes a single string argument;
    e.g. to convert the `max_age` value to an integer:
    ```
        max_age = get_parameter(name="max_age")
    ```

    A value must be provided for each parameter defined by `get_parameter()` *unless*
    a default value is specified.
    e.g. to default to 100 as the `max_age` value if no value is provided:
    ```
        max_age = get_parameter(name="max_age", default=100)
    ```

    To use in ehrQL:

    ```ehrql
    from ehrql import create_dataset, get_parameter
    from ehrql.tables.core import patients


    max_age = get_parameter(name="max_age", type=int, default=20)
    sex = get_parameter(name="sex", default="male")

    dataset = create_dataset()
    age = patients.age_on("2025-01-01")

    dataset.define_population((age < max_age) & (patients.sex==sex))
    ```
    """
    # allow_abbrev disables prefix matching, so we can use parse_known_args without
    # the risk of overeagerly matching other parameters (e.g. given user args
    # `--foo=1 --foobar=2`, --foobar will correctly match foobar rather than the
    # prefix foo.
    parser = ArgumentParser(allow_abbrev=False)

    if type in [list, set, tuple]:
        raise SystemExit(
            f"{sys.argv[0]} error: {type} is not a valid type\n\n"
            "To define a parameter as a sequence, define `get_parameter()` "
            " with a type applicable to a single string argument, e.g.\n\n"
            '\tget_parameter("sex", type=str)\n\n'
            "and pass multiple values to the generate-dataset command:\n\n"
            f"\tgenerate-dataset {sys.argv[0]} -- --sex male female"
        )

    # We use nargs="+" and action="extend" so we can return either a single value or a list,
    # depending on what values have been provided
    parser.add_argument(f"--{name}", type=type, action="extend", nargs="+", default=[])

    # Use parse_known_args so we can parse only this single parameter without raising errors
    # if there are other undefined args.
    namespace, _ = parser.parse_known_args(sys.argv[1:])
    value = getattr(namespace, name)
    if not value:
        if default is not None:
            return default
        raise SystemExit(
            f"{sys.argv[0]} error: parameter `{name}` defined but no values found. Pass parameters in the "
            f"form `--{name} <value>` or provide a default value to `get_parameter()`"
        )
    if len(value) == 1:
        value = value[0]
    logger.info("Parsed parameter: `%s` = %r", name, value)
    return value
