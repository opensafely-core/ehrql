import datetime

from ehrql.codes import DMDCode
from ehrql.tables import EventFrame, Series, table
from ehrql.tables.core import patients


__all__ = ["hospital_admissions", "patients", "prescriptions"]


@table
class hospital_admissions(EventFrame):
    # (admission_date,)
    # (primary_diagnosis,)
    # (admission_method,)
    # (episode_is_finished,)
    # spell_id
    ...


@table
class prescriptions(EventFrame):
    prescribed_dmd_code = Series(DMDCode)
    processing_date = Series(datetime.date)
