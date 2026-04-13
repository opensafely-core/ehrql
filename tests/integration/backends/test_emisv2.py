from datetime import date, datetime

from ehrql.backends.emisv2 import EMISV2Backend
from ehrql.tables import emisv2
from tests.backend_schemas.emisv2.schema import Patient

from .helpers import (
    register_test_for,
)


def test_extract_smoketest_dataset_definition(trino_engine):
    trino_engine.setup(
        # Trino DBAPI's Binary() implementation takes a string and encodes it as UTF-8
        Patient(
            _pk=1,
            patient_id=bytes(range(16)).decode("utf-8"),
            date_of_birth=datetime(2000, 1, 1, 0, 0, 0, 0),
        ),
        Patient(
            _pk=2,
            patient_id=bytes(range(1, 17)).decode("utf-8"),
            date_of_birth=datetime(1900, 1, 1, 0, 0, 0, 0),
        ),
    )

    # This query is a copy of the smoketest dataset definition query in
    # tests/acceptance/external_studies/test-age-distribution/analysis/dataset_definition.py
    from ehrql import create_dataset
    from ehrql.tables.smoketest import patients

    index_year = 2022
    min_age = 18
    max_age = 80

    year_of_birth = patients.date_of_birth.year
    age = index_year - year_of_birth

    dataset = create_dataset()
    dataset.define_population((age >= min_age) & (age <= max_age))
    dataset.age = age

    results = trino_engine.extract(dataset, backend=EMISV2Backend())

    assert results == [{"patient_id": bytes(range(16)), "age": 22}]


@register_test_for(emisv2.patients)
def test_patients(select_all_emisv2):
    results = select_all_emisv2(
        Patient(
            _pk=1,
            patient_id=bytes(range(16)).decode("utf-8"),
            date_of_birth=datetime(2000, 1, 1, 0, 0, 0, 0),
            date_of_death=datetime(2023, 5, 12, 0, 0, 0, 0),
            sex="M",
        ),
    )
    assert results == [
        {
            "patient_id": bytes(range(16)),
            "date_of_birth": date(2000, 1, 1),
            "date_of_death": date(2023, 5, 12),
            "sex": "male",
        }
    ]
