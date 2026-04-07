import datetime

import sqlalchemy
import sqlalchemy.orm

from tests.backend_schemas.emisv2.schema import Patient


def test_patient(trino_database):
    """
    Validate that the patient table is correctly defined.
    This is a temporary test since we do not have a EMIS v2 backend yet;
    when we have one, this test can be removed.
    """
    new_patient = Patient(
        _pk=1,
        # Trino DBAPI's Binary() implementation takes a string and encodes it as UTF-8
        patient_id=bytes(range(16)).decode("utf-8"),
        date_of_birth=datetime.datetime(2023, 5, 1, 0, 0, 0, 0),
    )

    trino_database.setup([new_patient])
    with sqlalchemy.orm.Session(trino_database.engine()) as session:
        result = session.execute(sqlalchemy.select(Patient)).scalar_one()

    assert result._pk == 1
    assert result.patient_id == bytes(range(16))
    assert result.date_of_birth == datetime.datetime(2023, 5, 1, 0, 0, 0, 0)
