import datetime

from databuilder.tables import EventFrame, Series, table

###
# The following contracts have not been through any kind of assurance process!
###


@table
class clinical_events(EventFrame):
    """TODO."""

    code = Series(str)
    system = Series(str)
    date = Series(datetime.date)
    numeric_value = Series(float)


@table
class hospital_admissions(EventFrame):
    """TODO."""

    admission_date = Series(datetime.date)
    primary_diagnosis = Series(str)
    admission_method = Series(int)
    episode_is_finished = Series(bool)
    spell_id = Series(int)


@table
class hospitalizations(EventFrame):
    """TODO."""

    date = Series(datetime.date)
    code = Series(str)
    system = Series(str)


@table
class hospitalizations_without_system(EventFrame):
    """TODO."""

    code = Series(str)


@table
class patient_address(EventFrame):
    """TODO."""

    patientaddress_id = Series(int)
    date_start = Series(datetime.date)
    date_end = Series(datetime.date)
    index_of_multiple_deprivation_rounded = Series(int)
    has_postcode = Series(bool)


@table
class practice_registrations(EventFrame):
    """TODO."""

    pseudo_id = Series(int)
    nuts1_region_name = Series(str)
    date_start = Series(datetime.date)
    date_end = Series(datetime.date)


@table
class prescriptions(EventFrame):
    """TODO."""

    prescribed_dmd_code = Series(str)
    processing_date = Series(datetime.date)


@table
class covid_test_results(EventFrame):
    """TODO."""

    date = Series(datetime.date)
    positive_result = Series(bool)


@table
class patients(EventFrame):
    """TODO."""

    date_of_birth = Series(datetime.date)
