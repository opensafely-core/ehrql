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

    new_medication_issue_record = schema.MedicationIssueRecord(
        patient_id=bytes(range(16)),
        dmd_product_code_id=12354611500001104,
        effective_datetime=datetime.datetime(
            2023, 5, 12, 14, 30, 15, 0, tzinfo=datetime.UTC
        ),
    )
    new_patient = schema.Patient(
        patient_id=bytes(range(16)),
        date_of_birth=datetime.datetime(2023, 5, 1, 0, 0, 0, 0),
    )
    new_observation = schema.Observation(
        patient_id=bytes(range(16)),
        effective_datetime=datetime.datetime(
            2023, 5, 12, 14, 30, 15, 0, tzinfo=datetime.UTC
        ),
        numeric_value=80.0,
        snomed_concept_id=123456789,
    )
    with sqlalchemy.orm.Session(engine) as session:
        session.add(new_medication_issue_record)
        session.add(new_patient)
        session.add(new_observation)
        session.commit()
        selected_medication_issue_record = session.execute(
            sqlalchemy.select(schema.MedicationIssueRecord)
        ).scalar_one()
        selected_patient = session.execute(
            sqlalchemy.select(schema.Patient)
        ).scalar_one()
        selected_observation = session.execute(
            sqlalchemy.select(schema.Observation)
        ).scalar_one()

    # SQLite does not support timezone-aware datetimes
    # so in these assertions we have to ignore the timezone
    assert selected_patient._pk == 1
    assert selected_patient.patient_id == bytes(range(16))
    assert selected_patient.date_of_birth == datetime.datetime(2023, 5, 1, 0, 0, 0, 0)

    assert selected_medication_issue_record._pk == 1
    assert selected_medication_issue_record.patient_id == bytes(range(16))
    assert selected_medication_issue_record.dmd_product_code_id == 12354611500001104
    assert selected_medication_issue_record.effective_datetime == datetime.datetime(
        2023, 5, 12, 14, 30, 15, 0
    )

    assert selected_observation._pk == 1
    assert selected_observation.patient_id == bytes(range(16))
    assert selected_observation.effective_datetime == datetime.datetime(
        2023, 5, 12, 14, 30, 15, 0
    )
    assert selected_observation.numeric_value == 80.0
    assert selected_observation.snomed_concept_id == 123456789

    engine.dispose()
