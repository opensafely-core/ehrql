import datetime

import pytest

import ehrql.tables
from ehrql import INTERVAL, create_measures, years
from ehrql.file_formats import (
    FILE_FORMATS,
    read_dataset,
    write_dataset,
)
from ehrql.query_language import BaseFrame, DummyDataConfig
from ehrql.query_model.column_specs import ColumnSpec
from ehrql.serializer import deserialize, serialize
from ehrql.tables.beta.core import clinical_events, patients
from ehrql.utils.module_utils import get_submodules


def as_query_model(query_lang_expr):
    return query_lang_expr._qm_node


def define_measure(*args, **kwargs):
    measures = create_measures()
    measures.define_measure(*args, **kwargs)
    return list(measures)


def get_all_tables():
    for module in get_submodules(ehrql.tables):
        yield from (
            as_query_model(frame)
            for frame in vars(module).values()
            if isinstance(frame, BaseFrame)
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
        # Test that we can serialize every table in every schema
        *get_all_tables(),
    ],
)
def test_roundtrip(value):
    assert value == deserialize(serialize(value))


# Fixture which generates a dataset reader instance for every format we support
@pytest.fixture(params=list(FILE_FORMATS.keys()))
def dataset_reader(request, tmp_path):
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
    filename = tmp_path / f"dataset{extension}"
    write_dataset(filename, data, specs)
    yield read_dataset(filename, specs)


def test_roundtrip_dataset_readers(dataset_reader):
    roundtripped = deserialize(serialize(dataset_reader))
    assert roundtripped is not dataset_reader
    assert roundtripped == dataset_reader
    assert list(roundtripped) == list(dataset_reader)
