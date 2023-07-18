#!/usr/bin/env python
"""
Attempts to de-duplicate query model structures by extracting repeated elements into
variables.

Usage looks like:

    * Copy the query model example into a file, assign it to `variable`, and add any
      imports needed.

    * Run `./simplify_query_model.py PATH_TO_FILE`.

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
import typing
from collections import defaultdict
from functools import singledispatchmethod

import black

from ehrql.main import load_module
from ehrql.query_model.nodes import (
    InlinePatientTable,
    Node,
    SelectColumn,
    SelectPatientTable,
    SelectTable,
)


TABLE_TYPES = SelectTable | SelectPatientTable | InlinePatientTable


VARIABLE_NAMES = ["population", "variable", "data"]


def main(filename, inplace=False):
    module = load_module(filename)
    namespace = vars(module)
    variables = {
        name: namespace.pop(name) for name in VARIABLE_NAMES if name in namespace
    }
    qm_repr = QueryModelRepr(namespace)
    variable_reprs = {name: qm_repr(value) for name, value in variables.items()}
    output = [get_imports(filename)]
    output.extend(
        [
            f"{name} = {reference_repr}"
            for name, reference_repr in qm_repr.reference_reprs.items()
        ]
    )
    for name, variable_repr in variable_reprs.items():
        output.append(f"{name} = {variable_repr}")
    code = "\n\n".join(output)
    code = black.format_str(code, mode=black.Mode())
    if inplace:
        filename.write_text(code)
        return ""
    else:
        return code


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
        for field in dataclasses.fields(value):
            if field.default is dataclasses.MISSING:
                assert (
                    not kwargs
                ), "Required fields must come before all optional fields"
                args.append(getattr(value, field.name))
            else:
                kwargs[field.name] = getattr(value, field.name)
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


def get_imports(filename):
    imports = []
    contents = filename.read_text()
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
        help="Path to a Python file which defines an object called `variable`",
    )
    parser.add_argument(
        "-i,--inplace",
        dest="inplace",
        action="store_true",
        help="Update the file in-place",
    )
    args = parser.parse_args()
    output = main(**vars(args))
    print(output, end="")
