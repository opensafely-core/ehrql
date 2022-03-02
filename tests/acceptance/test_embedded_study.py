from datetime import datetime

from tests.lib.fixtures import trivial_dataset_definition
from tests.lib.tpp_schema import patient


def test_generate_dataset(study, database):
    database.setup(patient(dob=datetime(1943, 5, 5)))

    study.setup_from_string(trivial_dataset_definition)
    study.run(database, "tpp")
    results = study.results()

    assert len(results) == 1
    assert results[0]["year"] == "1943"
