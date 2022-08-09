import datetime

from databuilder.query_language import PatientFrame, Series, construct


@construct
class patients(PatientFrame):
    date_of_birth = Series(datetime.date)
    date_of_death = Series(datetime.date)
    sex = Series(str)
