import pytest

from cohortextractor import table
from cohortextractor.backends import MockBackend
from cohortextractor.main import extract


@pytest.mark.integration
def test_pick_a_single_value(database, load_data):
    # setup SQL that insert into the source tables as defined in MockBackend
    sql = """
        DROP TABLE IF EXISTS events, practice_registrations;
        CREATE TABLE events (PatientId int, EventCode varchar(255), Date varchar(255));
        INSERT INTO events (PatientId, EventCode) VALUES (1, 'xyz');
        CREATE TABLE practice_registrations (PatientId int);
        INSERT INTO practice_registrations (PatientId) VALUES (1);
    """

    class Cohort:
        code = table("clinical_events").get("code")

    expected = [{"patient_id": 1, "code": "xyz"}]

    load_data(sql=sql)
    backend = MockBackend(database.host_url())
    actual = run_extraction(Cohort, backend)
    assert actual == expected


def run_extraction(cohort, backend):
    return list(extract(cohort, backend))
