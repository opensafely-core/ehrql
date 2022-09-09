import csv
import datetime
import functools
import gzip

from databuilder.column_specs import get_column_specs
from databuilder.file_formats import get_file_extension
from databuilder.query_language import compile


class ValidationError(Exception):
    pass


def validate_file_types_match(dummy_filename, output_filename):
    if get_file_extension(dummy_filename) != get_file_extension(output_filename):
        raise ValidationError(
            f"Dummy data file does not have the same file extension as the output "
            f"filename:\n"
            f"Dummy data file: {dummy_filename}\n"
            f"Output file: {output_filename}"
        )


def validate_dummy_data_file(dataset_definition, filename):
    variable_definitions = compile(dataset_definition)
    column_specs = get_column_specs(variable_definitions)

    extension = get_file_extension(filename)
    if extension not in (".csv", ".csv.gz"):
        raise ValidationError(f"Unsupported file type: {extension}")

    open_fn = gzip.open if extension.endswith(".gz") else open
    with open_fn(filename, mode="rt", newline="") as f:
        validate_csv_against_spec(f, column_specs)


def validate_csv_against_spec(csv_file, column_specs):
    reader = csv.DictReader(csv_file)
    validate_headers(reader.fieldnames, list(column_specs.keys()))
    empty_columns = set(reader.fieldnames)

    for row_n, row in enumerate(reader, start=1):
        # DictReader puts any unexpected columns under the key `None`
        if None in row:
            raise ValidationError(f"Too many columns on row {row_n}")

        for name, spec in column_specs.items():
            value = row[name]
            if value:
                empty_columns.discard(name)
            elif value is None:
                raise ValidationError(f"Too few columns on row {row_n}")

            try:
                validate_str_against_spec(value, spec)
            except ValidationError as e:
                message = f"row {row_n}, column {name!r}: {e}"
                raise ValidationError(message) from e

    # In the context of dummy data I think that an all-NULL column should be considered
    # an error, though it might not be strictly speaking invalid
    if empty_columns:
        raise ValidationError(f"Columns are empty: {', '.join(empty_columns)}")


def validate_headers(headers, expected_headers):
    headers_set = set(headers)
    expected_set = set(expected_headers)
    if headers_set != expected_set:
        errors = []
        missing = expected_set - headers_set
        if missing:
            errors.append(f"Missing columns: {', '.join(missing)}")
        extra = headers_set - expected_set
        if extra:
            errors.append(f"Unexpected columns: {', '.join(extra)}")
        raise ValidationError("\n".join(errors))
    elif headers != expected_headers:
        # We could be more relaxed about things here, but I think it's worth insisting
        # that columns be in the same order. We've seen analysis code before which is
        # sensitive to column ordering.
        raise ValidationError(
            f"Headers not in expected order:\n"
            f"  expected: {', '.join(expected_headers)}\n"
            f"  found: {', '.join(headers)}"
        )


def validate_str_against_spec(value, spec):
    if not value:
        if not spec.nullable:
            raise ValidationError("NULL value not allowed here")
        else:
            return
    # We can't call the singledispatch function directly as we don't have an instance
    # of the type, we just have the type itself. So we call `dispatch()` to find the
    # appropriate implementation.
    validate = validate_str_type.dispatch(spec.type)
    try:
        validate(spec.type, value)
    except ValidationError as e:
        detail = str(e)
        raise ValidationError(
            f"Invalid {spec.type.__name__}{', ' if detail else ''}{detail}: {value}"
        )


@functools.singledispatch
def validate_str_type(type_, value):
    assert False, f"Unhandled type: {type_}"


@validate_str_type.register(int)
@validate_str_type.register(float)
@validate_str_type.register(str)
def validate_str_as_type(type_, value):
    try:
        type_(value)
    except (TypeError, ValueError):
        raise ValidationError


@validate_str_type.register(bool)
def validate_str_as_bool(type_, value):
    if value not in ("0", "1"):
        raise ValidationError("must be '0' or '1'")


@validate_str_type.register(datetime.date)
def validate_str_as_date(type_, value):
    try:
        datetime.date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValidationError("must be in YYYY-MM-DD format")
