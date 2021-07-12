from cohort_lib import clinical_events


class Cohort:
    date = clinical_events().get("date")
    event = clinical_events().get("code")
