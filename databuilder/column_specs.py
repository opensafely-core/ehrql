import dataclasses

from databuilder.query_model import get_series_type


@dataclasses.dataclass(frozen=True)
class ColumnSpec:
    type: type  # noqa: A003
    nullable: bool = True


def get_column_specs(variable_definitions):
    """
    Given a dict of variable definitions return a dict of ColumnSpec objects, given the
    types (and other associated metadata) of all the columns in the output
    """
    # TODO: It may not be universally true that IDs are ints. Internally the EMIS IDs
    # are SHA512 hashes stored as hex strings which we convert to ints. But we can't
    # guarantee always to be able to pull this trick.
    column_specs = {"patient_id": ColumnSpec(int, nullable=False)}
    for name, series in variable_definitions.items():
        if name == "population":
            continue
        type_ = get_series_type(series)
        if hasattr(type_, "_primitive_type"):
            type_ = type_._primitive_type()
        column_specs[name] = ColumnSpec(type_, nullable=True)
    return column_specs
