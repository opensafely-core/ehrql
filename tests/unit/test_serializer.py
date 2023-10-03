import datetime

import pytest

from ehrql import INTERVAL, Measures, years
from ehrql.file_formats import (
    FILE_FORMATS,
    read_dataset,
    write_dataset,
)
from ehrql.query_language import DummyDataConfig
from ehrql.query_model.column_specs import ColumnSpec
from ehrql.serializer import deserialize, serialize
from ehrql.tables.beta.core import clinical_events, patients


def as_query_model(query_lang_expr):
    return query_lang_expr._qm_node


measures = Measures()
measures.define_measure(
    "test_measure",
    numerator=clinical_events.where(
        clinical_events.date.is_during(INTERVAL)
    ).count_for_patient(),
    denominator=patients.exists_for_patient(),
    group_by=dict(sex=patients.sex),
    intervals=years(3).starting_on("2020-01-01"),
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
        # Containers
        (1, 2, 3),
        frozenset([1, 2, 3]),
        {"foo": "bar"},
        # Dicts with non-string keys
        {("foo", 1): ("bar", 2)},
        # Type classes
        int,
        datetime.date,
        DummyDataConfig(population_size=10),
        # Basic query model structure
        as_query_model(
            clinical_events.where(
                clinical_events.date > patients.date_of_birth + years(10)
            )
            .sort_by(clinical_events.date)
            .first_for_patient()
            .numeric_value
        ),
        list(measures),
    ],
)
def test_roundtrip(value):
    assert value == deserialize(serialize(value))


def test_roundtrip_dataset_readers(dataset_reader):
    roundtripped = deserialize(serialize(dataset_reader))
    assert roundtripped == dataset_reader
    assert list(roundtripped) == list(dataset_reader)


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
