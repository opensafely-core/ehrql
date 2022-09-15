from datetime import datetime

from tests.lib.tpp_schema import patient


def test_generate_dataset(study, mssql_database):
    mssql_database.setup(
        patient(dob=datetime(1910, 5, 5)),
        patient(dob=datetime(1970, 5, 5)),
        patient(dob=datetime(1990, 5, 5)),
        patient(dob=datetime(2010, 5, 5)),
    )

    study.setup_from_repo(
        "opensafely/test-age-distribution",
        "main",
        "analysis/dataset_definition.py",
    )
    study.generate(mssql_database, "databuilder.backends.tpp.TPPBackend")
    results = study.results()

    assert len(results) == 2
    assert results[0]["age"] == "32"
