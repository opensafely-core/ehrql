import datetime
import inspect
import json
from pathlib import Path

import pytest

import ehrql.tables
from ehrql import INTERVAL, create_measures, years
from ehrql.file_formats import (
    FILE_FORMATS,
    read_rows,
    write_rows,
)
from ehrql.query_language import (
    DummyDataConfig,
    create_dataset,
    get_tables_from_namespace,
)
from ehrql.query_model.column_specs import ColumnSpec
from ehrql.query_model.nodes import InlinePatientTable, TableSchema
from ehrql.serializer import SerializerError, deserialize, serialize
from ehrql.tables.core import clinical_events, patients
from ehrql.utils.module_utils import get_submodules


def as_query_model(query_lang_expr):
    return query_lang_expr._qm_node


def define_measure(*args, **kwargs):
    measures = create_measures()
    measures.define_measure(*args, **kwargs)
    return measures._compile()


def get_all_tables():
    for module in get_submodules(ehrql.tables):
        yield from (
            as_query_model(frame) for _, frame in get_tables_from_namespace(module)
        )


@pytest.mark.parametrize(
    "value",
    [
        # Primitive types
        None,
        True,
        5,
        0.5,
        "foo",
        datetime.date(2023, 10, 2),
        # Container types
        (1, 2, 3),
        frozenset([1, 2, 3]),
        {"foo": "bar"},
        # Dicts with non-string keys
        {("foo", 1): ("bar", 2)},
        # Types
        int,
        datetime.date,
        # Misc stuff
        DummyDataConfig(population_size=10),
        # Basic query model structures
        as_query_model(
            clinical_events.where(
                clinical_events.date > patients.date_of_birth + years(10)
            )
            .sort_by(clinical_events.date)
            .first_for_patient()
            .numeric_value
        ),
        # Basic measures
        define_measure(
            "test_measure",
            numerator=clinical_events.where(
                clinical_events.date.is_during(INTERVAL)
            ).count_for_patient(),
            denominator=patients.exists_for_patient(),
            group_by=dict(sex=patients.sex),
            intervals=years(3).starting_on("2020-01-01"),
        ),
        # Most table definitions get serialized as references, but inline tables still need to
        # be serialized in full so we test them separately
        InlinePatientTable(
            rows=((1, "hello"), (2, "world")),
            schema=TableSchema.from_primitives(s=str),
        ),
        # Test that we can serialize every table in every schema
        *get_all_tables(),
    ],
)
def test_roundtrip(value):
    assert value == deserialize(serialize(value), root_dir=Path.cwd())


@pytest.mark.dummy_data
def test_dummy_data_config_roundtrip():
    dataset = create_dataset()
    kwargs = dict(
        population_size=100,
        legacy=False,
        timeout=100,
        additional_population_constraint=(patients.date_of_birth < "2000-01-01"),
    )
    dataset.configure_dummy_data(**kwargs)
    config = dataset.dummy_data_config
    assert config == deserialize(serialize(config), root_dir=Path.cwd())
    # Fail if we add new arguments to `configure_dummy_data` but don't exercise them
    # here
    assert set(kwargs) == set(
        inspect.signature(dataset.configure_dummy_data).parameters
    )


# Fixture which generates a rows reader instance for every format we support
@pytest.fixture(params=list(FILE_FORMATS.keys()))
def rows_reader(request, tmp_path):
    specs = {
        "patient_id": ColumnSpec(int, nullable=False),
        "b": ColumnSpec(bool),
        "i": ColumnSpec(int, min_value=10, max_value=20),
        "c": ColumnSpec(str, categories=("A", "B")),
    }

    data = [
        (123, True, 10, "A"),
        (456, None, 15, "B"),
        (789, False, 20, "A"),
    ]
    extension = request.param
    filename = tmp_path / f"some_file{extension}"
    write_rows(filename, data, specs)
    yield read_rows(filename, specs)


def test_roundtrip_rows_reader(rows_reader):
    parent_dir = rows_reader.filename.parent
    roundtripped = deserialize(serialize(rows_reader), root_dir=parent_dir)
    assert roundtripped is not rows_reader
    assert roundtripped == rows_reader
    assert list(roundtripped) == list(rows_reader)


def test_rows_reader_cannot_be_deserialized_outside_of_root_dir(rows_reader):
    serialized = serialize(rows_reader)
    with pytest.raises(SerializerError, match="is not contained within the directory"):
        deserialize(serialized, root_dir=Path("/some/path"))


@pytest.mark.parametrize("type_name", ["SelectTable", "SelectPatientTable"])
def test_prohibited_types_cannot_be_deserialized(type_name):
    structure = {
        "value": {type_name: {"name": "some_table", "schema": {"TableSchema": {}}}}
    }
    structure_json = json.dumps(structure)
    with pytest.raises(
        SerializerError,
        match=(
            "cannot be constructed directly but must be serialized as "
            "external references"
        ),
    ):
        deserialize(structure_json, root_dir=Path.cwd())
