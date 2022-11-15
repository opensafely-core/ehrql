import pytest
import sqlalchemy
import sqlalchemy.orm

from databuilder.orm_utils import orm_classes_from_ql_table_namespace
from databuilder.tables.beta import tpp


def test_case_statement(engine):
    if engine.name != "sqlite":
        pytest.skip()

    orm_classes = orm_classes_from_ql_table_namespace(tpp)
    engine.setup(metadata=orm_classes.Base.metadata)

    query = sqlalchemy.text(
        """
  WITH latest_vaccination AS (
                SELECT ordered_vaccinations.patient_id AS patient_id,
                       ordered_vaccinations.product_name AS product_name,
                       ordered_vaccinations.date AS date
                  FROM (
                        SELECT vaccinations.patient_id AS patient_id,
                               vaccinations.product_name AS product_name,
                               vaccinations.date AS date,
                               row_number() OVER (
                                PARTITION BY vaccinations.patient_id
                                    ORDER BY vaccinations.date DESC, vaccinations.product_name DESC
                               ) AS row_num
                          FROM vaccinations
                         WHERE date(vaccinations.date, '30 days')
                               <= '2022-06-01'
                       ) AS ordered_vaccinations
                 WHERE ordered_vaccinations.row_num = 1
             ),
       subsequent_admissions AS (
                SELECT DISTINCT hospital_admissions.patient_id AS patient_id
                  FROM hospital_admissions
                       JOIN latest_vaccination ON latest_vaccination.patient_id = hospital_admissions.patient_id
                 WHERE hospital_admissions.admission_date > latest_vaccination.date
                   AND hospital_admissions.admission_date
                       <= date(latest_vaccination.date, '30 days')
             )
SELECT patients.patient_id AS patient_id,
       latest_vaccination.date AS vaccination_date,
       latest_vaccination.product_name AS vaccination_product,
       subsequent_admissions.patient_id IS NOT NULL AS has_admission
  FROM patients
       LEFT JOIN latest_vaccination ON latest_vaccination.patient_id = patients.patient_id
       LEFT JOIN subsequent_admissions ON subsequent_admissions.patient_id = patients.patient_id
 WHERE patients.date_of_birth < '2000-01-01';
     """
    )

    with engine.sqlalchemy_engine().connect() as conn:
        results = list(conn.execute(query))
    assert not results
