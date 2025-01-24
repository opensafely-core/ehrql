"""
Attempts to de-duplicate query model structures by extracting repeated elements into
variables.

Usage looks like:

    * Copy the query model example (the `population`, `variable` and `data` arguments)
      into a file. Just copy the arguments as-is: don't worry about indendation,
      trailing commas or missing imports.

    * Run `python -m tests.lib.gentest_example_simplify PATH_TO_FILE`.

    * If the output looks vaguely sensible run the command again with the `--inplace`
      option to update the original file.

    * Table and column definitions should be automatically extracted, but other kinds of
      repeated structure will need to be extracted by hand. To do this: copy the
      structure, assign it to a variable, and re-run the above command.
"""

import argparse
import ast
import dataclasses
import pathlib
import re
import subprocess
import sys
import typing
from collections import defaultdict
from functools import singledispatchmethod

import ehrql.query_model.nodes
from ehrql.query_model.nodes import (
    InlinePatientTable,
    Node,
    SelectColumn,
    SelectPatientTable,
    SelectTable,
)


TABLE_TYPES = SelectTable | SelectPatientTable | InlinePatientTable


VARIABLE_NAMES = ["dataset", "data"]


def main(filename, output=False):  # pragma: no cover
    contents = filename.read_text()
    code = simplify(contents)
    if not output:
        filename.write_text(code)
        return ""
    else:
        return code


def simplify(contents):
    contents = fix_up_module(contents)
    namespace = {}
    exec(contents, namespace)
    variables = {
        name: fix_accidental_tuple(namespace.pop(name))
        for name in VARIABLE_NAMES
        if name in namespace
    }
    qm_repr = QueryModelRepr(namespace)
    variable_reprs = {name: qm_repr(value) for name, value in variables.items()}
    output = [get_imports(contents)]
    output.extend(
        [
            f"{name} = {reference_repr}"
            for name, reference_repr in qm_repr.reference_reprs.items()
        ]
    )
    for name, variable_repr in variable_reprs.items():
        output.append(f"{name} = {variable_repr}")
    code = "\n\n".join(output)
    code = ruff_format(code)
    return code


def ruff_format(code):
    process = subprocess.run(
        [sys.executable, "-m", "ruff", "format", "-"],
        check=True,
        text=True,
        capture_output=True,
        input=code,
    )
    return process.stdout


def fix_accidental_tuple(value):
    # Fix values where copying the Hypothesis example has left a trailing comma
    # resulting in an accidental tuple. The specific values we apply this to are never
    # intended to be tuples so we don't need to worry about false positives.
    if isinstance(value, tuple) and len(value) == 1:
        return value[0]
    return value


def fix_up_module(contents):
    "Apply some basic fixes to the module to make it importable"
    # If it has imports we assume it's been fixed up already
    if re.search(r"\bimport\b", contents):
        return contents
    names = "|".join(map(re.escape, VARIABLE_NAMES))
    # Strip leading indentation
    contents = re.sub(rf"^\s+({names})\s*=\s*", r"\1 = ", contents, flags=re.MULTILINE)
    # Add imports (many of these will be unnecessary but that's fine)
    imports = [
        "import datetime",
        "from tests.generative.test_query_model import data_setup, schema",
        f"from ehrql.query_model.nodes import ({', '.join(ehrql.query_model.nodes.__all__)})",
    ]
    contents = "\n".join(imports) + "\n" + contents
    return contents


class QueryModelRepr:
    def __init__(self, namespace):
        # Create an inverse mapping which maps each (hashable) value in the namespace to
        # the first name to which it's bound
        self.valuespace = {}
        for key, value in namespace.items():
            if not key.startswith("__") and isinstance(value, typing.Hashable):
                self.valuespace.setdefault(value, key)
        # Dict to record the repr of every value we use in `valuespace`
        self.reference_reprs = {}
        self.inline_table_number = defaultdict(iter(range(2**32)).__next__)

    def __call__(self, value):
        return self.repr(value)

    def repr(self, value):  # noqa: A003
        # If the value is already in the provided namespace then just use its name as
        # the repr
        if isinstance(value, typing.Hashable) and value in self.valuespace:
            name = self.valuespace[value]
            # Record the original repr of the value being referenced
            if name not in self.reference_reprs:
                self.reference_reprs[name] = self.repr_value(value)
            return name
        # Automatically create references for table definitions to avoid repeating them
        elif isinstance(value, TABLE_TYPES):
            self.valuespace[value] = self.table_name(value)
            return self.repr(value)
        # Automatically create references where columns are selected directly from
        # tables
        elif isinstance(value, SelectColumn) and isinstance(value.source, TABLE_TYPES):
            self.valuespace[value] = f"{self.table_name(value.source)}_{value.name}"
            return self.repr(value)
        else:
            return self.repr_value(value)

    def table_name(self, value):
        if isinstance(value, InlinePatientTable):
            return f"inline_{self.inline_table_number[value]}"
        else:
            return value.name

    @singledispatchmethod
    def repr_value(self, value):
        return repr(value)

    @repr_value.register(type)
    def repr_type(self, value):
        return f"{value.__module__}.{value.__qualname__}"

    @repr_value.register(Node)
    def repr_node(self, value):
        args = []
        kwargs = {}
        fields = dataclasses.fields(value)
        # Single argument nodes use positional arguments for brevity
        if len(fields) == 1:
            args = [getattr(value, fields[0].name)]
        else:
            kwargs = {field.name: getattr(value, field.name) for field in fields}
        return self.repr_init(value, args, kwargs)

    @repr_value.register(list)
    def repr_list(self, value):
        elements = [self.repr(v) for v in value]
        return f"[{', '.join(elements)}]"

    @repr_value.register(dict)
    def repr_dict(self, value):
        elements = [f"{self.repr(k)}: {self.repr(v)}" for k, v in value.items()]
        return f"{{{', '.join(elements)}}}"

    @repr_value.register(frozenset)
    def repr_frozenset(self, value):
        elements = [self.repr(v) for v in value]
        return f"frozenset({{{','.join(elements)}}})"

    @repr_value.register(tuple)
    def repr_tuple(self, value):
        elements = [self.repr(v) for v in value]
        if len(elements) == 1:
            return f"({elements[0]},)"
        else:
            return f"({','.join(elements)})"

    def repr_init(self, obj, args, kwargs):
        all_args = [self.repr(arg) for arg in args]
        all_args.extend(f"{key}={self.repr(value)}" for key, value in kwargs.items())
        name = obj.__class__.__qualname__
        return f"{name}({', '.join(all_args)})"


def get_imports(contents):
    imports = []
    for element in ast.parse(contents).body:
        if isinstance(element, ast.Import | ast.ImportFrom):
            imports.append(ast.unparse(element))
    return "\n".join(imports)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "filename",
        type=pathlib.Path,
        help="Path to a Python file containing a generative test example",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        action="store_true",
        help="Write file to stdout instead of updating it in-place",
    )
    args = parser.parse_args()
    output = main(**vars(args))
    print(output, end="")
