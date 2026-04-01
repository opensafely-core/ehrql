import datetime

import sqlalchemy
import sqlalchemy.orm

from tests.backend_schemas.emisv2 import schema


def test_schema():
    """
    Validate that the patient table is correctly defined.
    This is a temporary test since we do not have a EMIS v2 backend yet;
    when we have one, this test can be removed.
    """
    engine = sqlalchemy.create_engine("sqlite+pysqlite:///:memory:")
    schema.Base.metadata.create_all(engine)

    new_patient = schema.Patient(
        patient_id=bytes(range(16)),
        date_of_birth=datetime.datetime(2023, 5, 1, 0, 0, 0, 0),
    )
    with sqlalchemy.orm.Session(engine) as session:
        session.add(new_patient)
        session.commit()
        selected_patient = session.execute(
            sqlalchemy.select(schema.Patient)
        ).scalar_one()

    assert selected_patient._pk == 1
    assert selected_patient.patient_id == bytes(range(16))
    assert selected_patient.date_of_birth == datetime.datetime(2023, 5, 1, 0, 0, 0, 0)

    engine.dispose()
