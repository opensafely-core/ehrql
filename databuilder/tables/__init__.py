# TODO: This should probably be removed altogether but it's being used by the test
# study, and possibly by other example code others have written so I don't now is quite
# the right time to remove it.
# [1]: https://github.com/opensafely/test-age-distribution
import datetime

from databuilder.query_language import PatientFrame, Series, construct


@construct
class patients(PatientFrame):
    date_of_birth = Series(datetime.date)
    date_of_death = Series(datetime.date)
    sex = Series(str)
