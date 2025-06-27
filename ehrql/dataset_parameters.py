import sys
from argparse import ArgumentParser
from collections import Counter
from dataclasses import dataclass
from typing import Any


@dataclass
class Parameter:
    name: str
    type: callable = str
    default: Any | None = None


def get_dataset_parameters(*parameters: tuple[Parameter]):
    """
    Retrieve dataset definition parameters that have been passed on the command line.

    User parameters are passed after a --, in the format --key=value

    For example, to pass two arguments, max_age and sex:

    ```
    generate-dataset /path/to/dataset_definiton/.py --output /output/file \
        -- --max_age=70 --sex=female
    ```

    Define one or more `Parameter`s, e.g.:
    ```
        Parameter(name="max_age")
    ```
    Parameters are strings, with a default value None, unless explicitly specified, e.g.
    ```
        Parameter(name="max_age", type=int, default=100)
    ```

    To use in a dataset definition:

    ```
    from ehrql import create_dataset, get_dataset_parameters, Parameter

    parameters = get_dataset_parameters(
        Parameter(name="max_age", type=int, default=100),
        Parameter(name="sex", default="male")
    )

    dataset = create_dataset()
    age = patients.age_on("2025-01-01")
    sex = patients.sex

    dataset.define_population((age < parameters.max_age) & (sex==parameters.sex))
    ```
    """
    user_args = [arg.split("=")[0] for arg in sys.argv[1:]]
    counter = Counter(user_args)
    if max(counter.values()) > 1:
        dupes = ", ".join(k for k, v in counter.items() if v > 1)
        raise ValueError(f"Dataset parameters specified more than once: {dupes}")

    parser = ArgumentParser()

    for parameter in parameters:
        parser.add_argument(
            f"--{parameter.name}", type=parameter.type, default=parameter.default
        )
    return parser.parse_args()
