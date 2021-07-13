import pytest
from conftest import extract

from cohortextractor import table
from cohortextractor.backends import MockBackend


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
    actual = extract(Cohort, MockBackend, database)
    assert actual == expected
