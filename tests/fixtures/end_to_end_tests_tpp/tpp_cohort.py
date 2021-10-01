from cohort_lib import clinical_events


class Cohort:
    date = clinical_events().first_by("patient_id").get("date")
    event = clinical_events().first_by("patient_id").get("code")
