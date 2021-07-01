import pytest

from cohortextractor import table
from cohortextractor.main import extract


@pytest.mark.integration
def test_pick_a_single_value(database, load_data):
    sql = """
        DROP TABLE IF EXISTS clinical_events;
        CREATE TABLE clinical_events (patient_id int, code varchar(255));
        INSERT INTO clinical_events (patient_id, code) VALUES (1, 'xyz');
        GO
    """

    class Cohort:
        code = table("clinical_events").get("code")

    expected = [{"patient_id": 1, "code": "xyz"}]

    load_data(sql=sql)
    actual = run_extraction(Cohort, database)
    assert actual == expected


def run_extraction(cohort, database):
    return list(extract(cohort, database.host_url()))
