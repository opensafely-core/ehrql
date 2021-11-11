from cohortextractor.query_interface import QueryBuilder

from . import types
from .table_contract import Column, TableContract


class ClinicalEvents(QueryBuilder):
    code = "code"
    date = "date"

    def __init__(table_name):
        super().__init__("clinical_events")


clinical_events = ClinicalEvents()


class Patients(TableContract):
    """
    The Patients table holds personal details about the patient.
    """

    patient_id = Column(
        type=types.PseudoPatientId(),
        help=(
            "Patient's pseudonymous identifier, for linkage. You should not normally "
            "output or operate on this column"
        ),
    )
    date_of_birth = Column(
        type=types.Date(),
        help="The patient's date of birth",
    )
    sex = Column(
        type=types.Choice("F", "M"),
        help="The patient's sex",
    )
